from twisted.internet import reactor, ssl

from autobahn.twisted.websocket import WebSocketClientFactory, \
    WebSocketClientProtocol
from twisted.internet.protocol import ReconnectingClientFactory

import json
import sys
from threading import Thread

import logging

logger = logging.getLogger("Standalone_Mycroft_Client")
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel("INFO")

platform = "JarbasCliClientv0.1"


class JarbasClientProtocol(WebSocketClientProtocol):

    def onConnect(self, response):
        logger.info("Server connected: {0}".format(response.peer))

    def onOpen(self):
        logger.info("WebSocket connection open. ")
        self.input_loop = Thread(target=self.get_cli_input)
        self.input_loop.setDaemon(True)
        self.input_loop.start()

    def onMessage(self, payload, isBinary):
        if not isBinary:
            msg = json.loads(payload)
            if msg.get("type", "") == "speak":
                utterance = msg["data"]["utterance"]
                logger.info("Output: " + utterance)
            if msg.get("type", "") == "server.complete_intent_failure":
                logger.error("Output: complete_intent_failure")
        else:
            pass

    def onClose(self, wasClean, code, reason):
        logger.info("WebSocket connection closed: {0}".format(reason))

    # cli input thread
    def get_cli_input(self):
        while True:
            line = raw_input("Input: ")
            msg = {"data": {"utterances": [line], "lang": "en-us"},
                   "type": "recognizer_loop:utterance",
                   "context": {"source": self.peer, "destinatary":
                       "https_server", "platform": platform}}
            msg = json.dumps(msg)
            self.sendMessage(msg, False)


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