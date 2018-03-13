from twisted.internet import reactor, ssl

from autobahn.twisted.websocket import WebSocketClientFactory, \
    WebSocketClientProtocol
from twisted.internet.protocol import ReconnectingClientFactory

import json
from threading import Thread
import hclib
import sys
from time import sleep
import random
from mycroft.util.log import LOG as logger


platform = "JarbasHackChatClientv0.1"
username = "Jarbas"
hack_chat_channel = "JarbasAI"


class JarbasClientProtocol(WebSocketClientProtocol):
    hackchat = None
    online_users = []
    connector = None
    waiting_messages = []
    extra_delay = 0
    last_sent = ""

    def send_queued_message(self):
        while True:
            if len(self.waiting_messages):
                message = ""
                for idx, utterance in enumerate(self.waiting_messages):
                    if utterance:
                        message += utterance + "\n"
                    self.waiting_messages[idx] = ""
                    if len(message) >= 180:
                        words = message.split(" ")
                        new = ""
                        for idx, word in enumerate(words):
                            if len(new) < 180:
                                new += word + " "
                                words[idx] = ""
                        words = [w for w in words if w]
                        self.waiting_messages.insert(0, " ".join(words))
                        message = new
                        break

                if self.extra_delay:
                    sleep(self.extra_delay)
                logger.info("Sent: " + message)
                self.connector.send(message)
                self.last_sent = message
                sleep(random.choice([1,1.2,1.5,1.7,2,2.2,3,2.6]))
                self.waiting_messages = [ut for ut in self.waiting_messages
                                         if ut]
            else:
                sleep(1)

    def start_hack_chat(self):
        self.hackchat = hclib.HackChat(self.on_hack_message, username,
                                       hack_chat_channel)

    # Make a callback function with two parameters.
    def on_hack_message(self, connector, data):
        # The second parameter (<data>) is the data received.
        self.connector = connector
        self.online_users = connector.onlineUsers
        user = data.get("nick", "")
        if user and user == username:
            # dont answer self
            return
        # Checks if we are being limited
        if data["type"] == "warn":
            logger.warning(data["warning"])
            self.extra_delay = 5
            # resend failed
            self.waiting_messages.insert(0, self.last_sent)
        # Checks if someone joined the channel.
        elif data["type"] == "online add":
            # Sends a greeting the person joining the channel.
            #
            connector.send("Hello {}".format(user))
        elif data["type"] == "message":
            utterance = data["text"]
            if utterance == "stop":
                self.waiting_messages = []
                connector.send("ok, stopped")
                return
            msg = {"data": {"utterances": [utterance], "lang": "en-us"},
                   "type": "recognizer_loop:utterance",
                   "context": {"source": self.peer, "destinatary":
                       "https_server", "platform": platform,
                               "hack_chat_nick": user, "user": user,
                               "target": "hackchat"}}
            msg = json.dumps(msg)
            self.sendMessage(msg, False)
        else:
            print data

    def onConnect(self, response):
        logger.info("Server connected: {0}".format(response.peer))

    def onOpen(self):
        logger.info("WebSocket connection open. ")
        self.chat_thread = Thread(target=self.start_hack_chat)
        self.chat_thread.setDaemon(True)
        self.chat_thread.start()

        self.message_thread = Thread(target=self.send_queued_message)
        self.message_thread.setDaemon(True)
        self.message_thread.start()

    def onMessage(self, payload, isBinary):
        if not isBinary:
            msg = json.loads(payload)
            user = msg.get("context", {}).get("hack_chat_nick", "")
            if user not in self.online_users:
                logger.info("invalid hack chat user: " + user)
                return
            utterance = ""
            if msg.get("type", "") == "speak":
                utterance = msg["data"]["utterance"]
            elif msg.get("type", "") == "server.complete_intent_failure":
                utterance = "i can't answer that yet"

            if utterance:
                utterance = "@{} , ".format(user) + utterance
                self.waiting_messages.append(utterance)
                logger.info("Queued: " + utterance)
        else:
            pass

    def onClose(self, wasClean, code, reason):
        logger.info("WebSocket connection closed: {0}".format(reason))
        if self.hackchat is not None:
            self.hackchat.leave()
        self.message_thread.join()
        self.chat_thread.join()
        self.hackchat = None
        self.online_users = []
        self.connector = None
        sys.exit()


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