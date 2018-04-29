from twisted.internet import reactor, ssl

from autobahn.twisted.websocket import WebSocketClientFactory, \
    WebSocketClientProtocol
from twisted.internet.protocol import ReconnectingClientFactory

import json
from threading import Thread
import base64
from fbchat.utils import Message
from fbchat import log, Client
from time import sleep

platform = "JarbasFacebookChatClientv0.1"


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


class JarbasFacebookClientProtocol(WebSocketClientProtocol):
    facebook = None
    clients = {}

    def start_fb_chat(self):
        self.facebook = FaceBot(self.mail, self.password)
        self.facebook.listen()

    def onConnect(self, response):
        print("Server connected: {0}".format(response.peer))

    def onOpen(self):
        print("WebSocket connection open. ")
        self.mail = self.factory.mail
        self.password = self.factory.password
        self.chat_thread = Thread(target=self.start_fb_chat)
        self.chat_thread.setDaemon(True)
        self.chat_thread.start()
        while self.facebook is None:
            sleep(1)
        self.facebook.bind(self)
        self.factory.client = self

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
        print("WebSocket connection closed: {0}".format(reason))


class JarbasFacebookClientFactory(WebSocketClientFactory, ReconnectingClientFactory):
    protocol = JarbasFacebookClientProtocol

    def __init__(self, mail, password, *args, **kwargs):
        super(JarbasFacebookClientFactory, self).__init__(*args, **kwargs)
        self.status = "disconnected"
        self.client = None
        self.mail = mail
        self.password = password

    # websocket handlers
    def clientConnectionFailed(self, connector, reason):
        print("Client connection failed: " + str(reason) + " .. retrying ..")
        self.status = "disconnected"
        self.retry(connector)

    def clientConnectionLost(self, connector, reason):
        print("Client connection lost: " + str(reason) + " .. retrying ..")
        self.status = "disconnected"
        self.retry(connector)


def connect_to_facebook(mail, password, host="127.0.0.1", port=5678, name="jarbas facebook bridge", api="test_key"):
    authorization = name + ":" + api
    usernamePasswordDecoded = authorization
    api = base64.b64encode(usernamePasswordDecoded)
    headers = {'authorization': api}
    address = u"wss://" + host + u":" + str(port)
    factory = JarbasFacebookClientFactory(mail, password, address, headers=headers, useragent=platform)
    factory.protocol = JarbasFacebookClientProtocol
    contextFactory = ssl.ClientContextFactory()
    reactor.connectSSL(host, port, factory, contextFactory)
    reactor.run()
