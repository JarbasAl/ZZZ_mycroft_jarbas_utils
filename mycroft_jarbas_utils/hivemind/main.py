from os.path import exists, dirname
from threading import Thread
import os
from twisted.internet import reactor, ssl
from autobahn.twisted.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory
from mycroft.messagebus.client.ws import WebsocketClient
from mycroft.messagebus.message import Message
from mycroft.util.log import LOG as logger
from mycroft.configuration import Configuration
from mycroft.util.ssl.self_signed import create_self_signed_cert
from mycroft_jarbas_utils.hivemind.database.user import UserDatabase

author = "jarbas"

NAME = Configuration.get().get("hivemind", {}).get("name", "JarbasServer")


def root_dir():
    """ Returns root directory for this project """
    return os.path.dirname(os.path.realpath(__file__ + '/.'))


users = UserDatabase()


# protocol
class JarbasServerProtocol(WebSocketServerProtocol):
    def onConnect(self, request):
        import base64
        logger.info("Client connecting: {0}".format(request.peer))
        # validate user
        usernamePasswordEncoded = request.headers.get("authorization")
        usernamePasswordEncoded = usernamePasswordEncoded
        usernamePasswordDecoded = base64.b64decode(usernamePasswordEncoded)
        name, api = usernamePasswordDecoded.split(":")
        ip = " "  # request.peer.split(":")[1]
        context = {"source": self.peer}
        self.platform = request.headers.get("platform", "unknown")
        user = users.get_user_by_api_key(api)
        if not user:
            logger.info("Client provided an invalid api key")
            self.factory.emitter_send("client.connection.error",
                                      {"error": "invalid api key",
                                       "ip": ip,
                                       "api_key": api},
                                      context)
            raise ValueError("Invalid API key")
        # send message to internal mycroft bus
        data = {"ip": ip, "headers": request.headers}
        self.factory.emitter_send("client.connect", data, context)
        # return a pair with WS protocol spoken (or None for any) and
        # custom headers to send in initial WS opening handshake HTTP response
        headers = {"hivemind": NAME}
        return (None, headers)

    def onOpen(self):
        """
       Connection from client is opened. Fires after opening
       websockets handshake has been completed and we can send
       and receive messages.

       Register client in factory, so that it is able to track it.
       """
        self.factory.register_client(self, self.platform)
        logger.info("WebSocket connection open.")

    def onMessage(self, payload, isBinary):
        if isBinary:
            logger.info("Binary message received: {0} bytes".format(len(payload)))
        else:
            logger.info("Text message received: {0}".format(payload.decode('utf8')))

        self.factory.process_message(self, payload, isBinary)

    def onClose(self, wasClean, code, reason):
        self.factory.unregister_client(self, reason=u"connection closed")
        logger.info("WebSocket connection closed: {0}".format(reason))
        ip = " "  # self.peer.split(":")[1]
        data = {"ip": ip, "code": code, "reason": "connection closed", "wasClean": wasClean}
        context = {"source": self.peer}
        self.factory.emitter_send("client.disconnect", data, context)

    def connectionLost(self, reason):
        """
       Client lost connection, either disconnected or some error.
       Remove client from list of tracked connections.
       """
        self.factory.unregister_client(self, reason=u"connection lost")
        logger.info("WebSocket connection lost: {0}".format(reason))
        ip = " "  # self.peer.split(":")[1]
        data = {"ip": ip, "reason": "connection lost"}
        context = {"source": self.peer}
        self.factory.emitter_send("client.disconnect", data, context)


# hivemind internals
class JarbasServerFactory(WebSocketServerFactory):
    def __init__(self, *args, **kwargs):
        super(JarbasServerFactory, self).__init__(*args, **kwargs)
        # list of clients
        self.clients = {}
        # ip block policy
        self.ip_list = []
        self.blacklist = True  # if False, ip_list is a whitelist
        # mycroft_ws
        self.emitter = None
        self.emitter_thread = None
        self.create_internal_emitter()

    def emitter_send(self, type, data=None, context=None):
        data = data or {}
        context = context or {}
        self.emitter.emit(Message(type, data, context))

    def connect_to_internal_emitter(self):
        self.emitter.run_forever()

    def create_internal_emitter(self):
        # connect to mycroft internal websocket
        self.emitter = WebsocketClient()
        self.register_internal_messages()
        self.emitter_thread = Thread(target=self.connect_to_internal_emitter)
        self.emitter_thread.setDaemon(True)
        self.emitter_thread.start()

    def register_internal_messages(self):
        # catch all messages
        self.emitter.on('message', self.handle_message)
        self.emitter.on('client.broadcast', self.handle_broadcast)
        self.emitter.on('client.send', self.handle_send)

    # websocket handlers
    def register_client(self, client, platform=None):
        """
       Add client to list of managed connections.
       """
        platform = platform or "unknown"
        logger.info("registering client: " + str(client.peer))
        t, ip, sock = " ", "", ""  # client.peer.split(":")
        # see if ip adress is blacklisted
        if ip in self.ip_list and self.blacklist:
            logger.warning("Blacklisted ip tried to connect: " + ip)
            self.unregister_client(client, reason=u"Blacklisted ip")
            return
        # see if ip adress is whitelisted
        elif ip not in self.ip_list and not self.blacklist:
            logger.warning("Unknown ip tried to connect: " + ip)
            #  if not whitelisted kick
            self.unregister_client(client, reason=u"Unknown ip")
            return
        self.clients[client.peer] = {"object": client, "status":
            "connected", "platform": platform}

    def unregister_client(self, client, code=3078, reason=u"unregister client request"):
        """
       Remove client from list of managed connections.
       """
        logger.info("deregistering client: " + str(client.peer))
        if client.peer in self.clients.keys():
            client_data = self.clients[client.peer] or {}
            j, ip, sock_num = " ", "", ""  # client.peer.split(":")
            context = {"user": client_data.get("names", ["unknown_user"])[0],
                       "source": client.peer}
            self.emitter.emit(
                Message("user.disconnect",
                        {"reason": reason, "ip": ip, "sock": sock_num},
                        context))
            client.sendClose(code, reason)
            self.clients.pop(client.peer)

    def process_message(self, client, payload, isBinary):
        """
       Process message from client, decide what to do internally here
       """
        logger.info("processing message from client: " + str(client.peer))
        client_data = self.clients[client.peer]
        # client_protocol, ip, sock_num = client.peer.split(":")
        # TODO this would be the place to check for blacklisted
        # messages/skills/intents per user

        if isBinary:
            # TODO receive files
            pass
        else:
            # add context for this message
            message = Message.deserialize(payload)
            message.context["source"] = client.peer
            message.context["destinatary"] = "skills"
            if "platform" not in message.context:
                message.context["platform"] = client_data.get("platform",
                                                              "unknown")
            # send client message to internal mycroft bus
            self.emitter.emit(message)

    # mycroft handlers
    def handle_send(self, message):
        # send message to client
        msg = message.data.get("payload")
        is_file = message.data.get("isBinary")
        peer = message.data.get("peer")
        if is_file:
            # TODO send file
            pass
        elif peer in self.clients:
            # send message to client
            client = self.clients[peer]
            payload = Message.serialize(msg)
            client.sendMessage(payload, False)
        else:
            logger.error("That client is not connected")
            self.emitter_send("client.send.error",
                              {"error": "That client is not connected",
                               "peer": peer},
                              message.context)

    def handle_broadcast(self, message):
        # send message to all clients
        msg = message.data.get("payload")
        is_file = message.data.get("isBinary")
        if is_file:
            # TODO send file
            pass
        else:
            # send message to all clients
            server_msg = Message.serialize(msg)
            self.broadcast(server_msg)

    def handle_message(self, message):
        # forward internal messages to clients if they are the target
        message = Message.deserialize(message)
        if message.type == "complete_intent_failure":
            message.type = "hivemind.complete_intent_failure"
        message.context = message.context or {}
        peer = message.context.get("destinatary")
        if peer and peer in self.clients:
            client_data = self.clients[peer] or {}
            client = client_data.get("object")
            client.sendMessage(message.serialize(), False)


if __name__ == '__main__':

    # hivemind
    config = Configuration.get().get("hivemind", {})
    host = config.get("host", "0.0.0.0")
    port = config.get("port", 5678)
    max_connections = config.get("max_connections", -1)
    adress = u"wss://" + unicode(host) + u":" + unicode(port)
    cert = config.get("cert_file",
                      dirname(__file__) + '/certs/JarbasServer.crt')
    key = config.get("key_file",
                     dirname(__file__) + '/certs/JarbasServer.key')

    factory = JarbasServerFactory(adress)
    factory.protocol = JarbasServerProtocol
    if max_connections >= 0:
        factory.setProtocolOptions(maxConnections=max_connections)

    if not exists(key) or not exists(cert):
        logger.warning("ssl keys dont exist, creating self signed")
        dir = dirname(__file__) + "/certs"
        name = key.split("/")[-1].replace(".key", "")
        create_self_signed_cert(dir, name)
        cert = dir + "/" + name + ".crt"
        key = dir + "/" + name + ".key"
        logger.info("key created at: " + key)
        logger.info("crt created at: " + cert)
        # update config with new keys
        config["cert_file"] = cert
        config["key_file"] = key
        factory.config_update({"jarbas_server": config}, True)

    # SSL hivemind context: load hivemind key and certificate
    contextFactory = ssl.DefaultOpenSSLContextFactory(key, cert)

    reactor.listenSSL(port, factory, contextFactory)
    reactor.run()
