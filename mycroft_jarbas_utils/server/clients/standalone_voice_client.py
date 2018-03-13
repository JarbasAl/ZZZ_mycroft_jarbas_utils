from twisted.internet import reactor, ssl

from autobahn.twisted.websocket import WebSocketClientFactory, \
    WebSocketClientProtocol
from twisted.internet.protocol import ReconnectingClientFactory

import json
import sys
import speech_recognition as sr
import logging

logger = logging.getLogger("Standalone_Mycroft_Client")
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel("INFO")

platform = "JarbasVoiceClientv0.1"


class JarbasClientProtocol(WebSocketClientProtocol):
    def onConnect(self, response):
        logger.info("Server connected: {0}".format(response.peer))

    def onOpen(self):
        logger.info("WebSocket connection open. ")
        self.factory.client = self
        self.factory.start_listening()

    def onMessage(self, payload, isBinary):
        if not isBinary:
            msg = json.loads(payload)
            if msg.get("type", "") == "speak":
                utterance = msg["data"]["utterance"]
                logger.info("Output: " + utterance)
        else:
            pass

    def onClose(self, wasClean, code, reason):
        logger.info("WebSocket connection closed: {0}".format(reason))
        self.factory.stop_listening()


class JarbasClientFactory(WebSocketClientFactory, ReconnectingClientFactory):
    protocol = JarbasClientProtocol

    def __init__(self, *args, **kwargs):
        super(JarbasClientFactory, self).__init__(*args, **kwargs)
        self.status = "disconnected"
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.stop_listening = None
        self.client = None

    def start_listening(self):
        with self.microphone as source:
            # we only need to calibrate once, before we start listening
            self.recognizer.adjust_for_ambient_noise(source)
        # start listening in the background (note that we don't have to do this inside a `with` statement)
        self.stop_listening = self.recognizer.listen_in_background(
            self.microphone, self.process_voice)
        # `stop_listening` is now a function that, when called, stops background listening

    def process_voice(self, recognizer, audio):
        # received audio data, now we'll recognize it using Google Speech Recognition
        try:
            # for testing purposes, we're just using the default API key
            # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
            # instead of `r.recognize_google(audio)`
            line = recognizer.recognize_google(audio)
            logger.info(
                "Google Speech Recognition thinks you said " + line)
            msg = {"data": {"utterances": [line], "lang": "en-us"},
                   "type": "recognizer_loop:utterance",
                   "context": {"source": self.peer, "destinatary":
                       "https_server", "platform": platform}}
            msg = json.dumps(msg)
            self.client.sendMessage(msg, False)
        except sr.UnknownValueError:
            logger.info(
                "Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            logger.info(
                "Could not request results from Google Speech Recognition service; {0}".format(
                    e))


    # websocket handlers
    def clientConnectionFailed(self, connector, reason):
        logger.info(
            "Client connection failed: " + str(reason) + " .. retrying ..")
        self.status = "disconnected"
        self.retry(connector)

    def clientConnectionLost(self, connector, reason):
        logger.info(
            "Client connection lost: " + str(reason) + " .. retrying ..")
        self.status = "disconnected"
        self.retry(connector)


if __name__ == '__main__':
    import base64

    host = "127.0.0.1"
    port = 5678
    name = "standalone cli client"
    api = "test_key"
    authorization = name + ":" + api
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
