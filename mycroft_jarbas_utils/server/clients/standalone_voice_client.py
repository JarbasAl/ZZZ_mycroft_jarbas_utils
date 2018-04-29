from twisted.internet import reactor, ssl

from autobahn.twisted.websocket import WebSocketClientFactory, \
    WebSocketClientProtocol
from twisted.internet.protocol import ReconnectingClientFactory

from mycroft_jarbas_utils.server.clients.speech.listener import RecognizerLoop
from threading import Thread

conf = {
    "listener": {
        "sample_rate": 16000,
        "channels": 1,
        "record_wake_words": False,
        "record_utterances": False,
        "phoneme_duration": 120,
        "multiplier": 1.0,
        "energy_ratio": 1.5,
        "wake_word": "hey mycroft",
        "stand_up_word": "wake up"
    },
    "hotwords": {
        "hey mycroft": {
            "module": "pocketsphinx",
            "phonemes": "HH EY . M AY K R AO F T",
            "threshold": 1e-90,
            "lang": "en-us"
        },
        "thank you": {
            "module": "pocketsphinx",
            "phonemes": "TH AE NG K . Y UW .",
            "threshold": 1e-1,
            "listen": False,
            "utterance": "thank you",
            "active": True,
            "sound": "",
            "lang": "en-us"
        },
        "wake up": {
            "module": "pocketsphinx",
            "phonemes": "W EY K . AH P",
            "threshold": 1e-20,
            "lang": "en-us"
        }
    },
    "stt": {
        "deepspeech_server": {
            "uri": "http://localhost:8080/stt"
        },
        "kaldi": {
            "uri": "http://localhost:8080/client/dynamic/recognize"
        }
    }
}

import json
import sys
import logging
import base64

logger = logging.getLogger("Standalone_Mycroft_Client")
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel("INFO")

platform = "JarbasVoiceClientv0.1"


class JarbasVoiceClientProtocol(WebSocketClientProtocol):

    def onConnect(self, response):
        logger.info("Server connected: {0}".format(response.peer))

    def onOpen(self):
        logger.info("WebSocket connection open. ")
        self.loop = RecognizerLoop(conf)
        self.listen = Thread(target=self.start_listening)
        self.listen.setDaemon(True)
        self.listen.start()

    def handle_record_begin(self):
        logger.info("Begin Recording...")

    def handle_record_end(self):
        logger.info("End Recording...")

    def handle_awoken(self):
        """ Forward mycroft.awoken to the messagebus. """
        logger.info("Listener is now Awake: ")

    def handle_wakeword(self, event):
        logger.info("Wakeword Detected: " + event['utterance'])

    def handle_utterance(self, event):
        context = {'client_name': platform, "source": self.peer + ":speech",
                   'destinatary': "https_server"}
        msg = {"data": {"utterances": event['utterances'], "lang": "en-us"},
               "type": "recognizer_loop:utterance",
               "context": context}

        self.send(msg)

    def handle_unknown(self):
        logger.info('mycroft.speech.recognition.unknown')

    def handle_hotword(self, event):
        config = conf.get("listener", {})
        ww = config.get("wake_word", "hey mycroft")
        suw = config.get("stand_up_word", "wake up")
        if event["hotword"] != ww and event["hotword"] != suw:
            logger.info("Hotword Detected: " + event['hotword'])

    def handle_sleep(self):
        self.loop.sleep()

    def handle_wake_up(self, event):
        self.loop.awaken()

    def handle_mic_mute(self, event):
        self.loop.mute()

    def handle_mic_unmute(self, event):
        self.loop.unmute()

    def handle_audio_start(self, event):
        """
            Mute recognizer loop
        """
        self.loop.mute()

    def handle_audio_end(self, event):
        """
            Request unmute, if more sources has requested the mic to be muted
            it will remain muted.
        """
        self.loop.unmute()  # restore

    def handle_stop(self, event):
        """
            Handler for mycroft.stop, i.e. button press
        """
        self.loop.force_unmute()

    def start_listening(self):
        self.loop.on('recognizer_loop:utterance', self.handle_utterance)
        self.loop.on('recognizer_loop:record_begin', self.handle_record_begin)
        self.loop.on('recognizer_loop:awoken', self.handle_awoken)
        self.loop.on('recognizer_loop:wakeword', self.handle_wakeword)
        self.loop.on('recognizer_loop:hotword', self.handle_hotword)
        self.loop.on('recognizer_loop:record_end', self.handle_record_end)
        self.loop.run()

    def stop_listening(self):
        self.loop.remove_listener('recognizer_loop:utterance', self.handle_utterance)
        self.loop.remove_listener('recognizer_loop:record_begin', self.handle_record_begin)
        self.loop.remove_listener('recognizer_loop:awoken', self.handle_awoken)
        self.loop.remove_listener('recognizer_loop:wakeword', self.handle_wakeword)
        self.loop.remove_listener('recognizer_loop:hotword', self.handle_hotword)
        self.loop.remove_listener('recognizer_loop:record_end', self.handle_record_end)
        self.listen.join(0)

    def onMessage(self, payload, isBinary):
        if not isBinary:
            msg = json.loads(payload)
            if msg.get("type", "") == "speak":
                utterance = msg["data"]["utterance"]
                logger.info("Output: " + utterance)
        else:
            pass

    def send(self, msg):
        msg = json.dumps(msg)
        self.sendMessage(msg, False)

    def onClose(self, wasClean, code, reason):
        logger.info("WebSocket connection closed: {0}".format(reason))
        self.stop_listening()


class JarbasVoiceClientFactory(WebSocketClientFactory, ReconnectingClientFactory):
    protocol = JarbasVoiceClientProtocol

    def __init__(self, *args, **kwargs):
        super(JarbasVoiceClientFactory, self).__init__(*args, **kwargs)
        self.status = "disconnected"
        self.client = None

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


def start_voice_client(host="0.0.0.0", port=5678, name="standalone voice client", api="test_key", config=None):
    global conf
    conf = config or conf
    authorization = name + ":" + api
    usernamePasswordDecoded = authorization
    api = base64.b64encode(usernamePasswordDecoded)
    headers = {'authorization': api}
    adress = u"wss://" + host + u":" + str(port)
    factory = JarbasVoiceClientFactory(adress, headers=headers,
                                       useragent=platform)
    factory.protocol = JarbasVoiceClientProtocol
    contextFactory = ssl.ClientContextFactory()
    reactor.connectSSL(host, port, factory, contextFactory)
    reactor.run()


if __name__ == '__main__':
    start_voice_client()
