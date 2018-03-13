from twisted.internet import reactor, ssl

from autobahn.twisted.websocket import WebSocketClientFactory, \
    WebSocketClientProtocol
from twisted.internet.protocol import ReconnectingClientFactory

import json
from threading import Thread
import sys
from mycroft.util.log import LOG as logger

from fbchat.utils import Message

platform = "JarbasFacebookChatClientv0.1"
MAIL = "jarbasai@mailfence.com"
PASSWD = "SECRET"
from fbchat import log, Client
from time import sleep

# Subclass fbchat.Client and override required methods
class FaceBot(Client):
    protocol = None

    def bind(self, protocol):
        self.protocol = protocol

    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
        self.markAsDelivered(author_id, thread_id)
        self.markAsRead(author_id)

        log.info("{} from {} in {}".format(message_object, thread_id, thread_type.name))

        # If you're not the author, echo
        if author_id != self.uid:
            msg = {"data": {"utterances": [message_object.text], "lang":
                "en-us"},
                   "type": "recognizer_loop:utterance",
                   "context": {"source": self.protocol.peer, "destinatary":
                       "https_server", "platform": platform, "user":
                       author_id, "fb_chat_id": author_id, "target":
                       "fbchat"}}
            msg = json.dumps(msg)
            self.protocol.clients[author_id] = {"type": thread_type}
            self.protocol.sendMessage(msg, False)


class JarbasClientProtocol(WebSocketClientProtocol):
    facebook = None
    clients = {}

    def start_fb_chat(self):
        self.facebook = FaceBot(MAIL, PASSWD)
        self.facebook.listen()

    def onConnect(self, response):
        logger.info("Server connected: {0}".format(response.peer))

    def onOpen(self):
        logger.info("WebSocket connection open. ")

        self.chat_thread = Thread(target=self.start_fb_chat)
        self.chat_thread.setDaemon(True)
        self.chat_thread.start()
        while self.facebook is None:
            sleep(1)
        self.facebook.bind(self)

    def onMessage(self, payload, isBinary):
        if not isBinary:
            msg = json.loads(payload)
            utterance = ""
            if msg.get("type", "") == "speak":
                utterance = msg["data"]["utterance"]
            elif msg.get("type", "") == "server.complete_intent_failure":
                utterance = "i can't answer that yet"

            if utterance:
                user_id = msg["context"]["fb_chat_id"]
                self.facebook.send(Message(text=utterance),
                                   thread_id=user_id,
                                   thread_type=self.clients[user_id]["type"])
        else:
            pass

    def onClose(self, wasClean, code, reason):
        logger.info("WebSocket connection closed: {0}".format(reason))


class JarbasClientFactory(WebSocketClientFactory, ReconnectingClientFactory):
    protocol = JarbasClientProtocol

    def __init__(self, *args, **kwargs):
        super(JarbasClientFactory, self).__init__(*args, **kwargs)
        self.status = "disconnected"

    # websocket handlers
    def clientConnectionFailed(self, connector, reason):
        logger.info("Client connection failed: " + str(reason) + " .. retrying ..")
        self.status = "disconnected"
        self.retry(connector)

    def clientConnectionLost(self, connector, reason):
        logger.info("Client connection lost: " + str(reason) + " .. retrying ..")
        self.status = "disconnected"
        self.retry(connector)


if __name__ == '__main__':
    import base64
    host = "165.227.224.64"
    port = 5678
    name = "standalone cli client"
    api ="test_key"
    authorization = name+":"+api
    usernamePasswordDecoded = authorization
    api = base64.b64encode(usernamePasswordDecoded)
    headers = {'authorization': api}
    adress = u"wss://" + host + u":" + str(port)
    factory = JarbasClientFactory(adress, headers=headers,
                                  useragent=platform)
    factory.protocol = JarbasClientProtocol
    contextFactory = ssl.ClientContextFactory()
    reactor.connectSSL(host, port, factory, contextFactory)
    reactor.run()