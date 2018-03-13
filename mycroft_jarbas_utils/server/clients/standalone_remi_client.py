from remi import start, App, gui
import random
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

platform = "JarbasREMIClientv0.1"


class JarbasClientProtocol(WebSocketClientProtocol):
    remi = None

    def onConnect(self, response):
        logger.info("Server connected: {0}".format(response.peer))

    def onOpen(self):
        logger.info("WebSocket connection open. ")
        RemiClient.protocol = self

    def onMessage(self, payload, isBinary):
        if not isBinary:
            msg = json.loads(payload)
            if msg.get("type", "") == "speak":
                utterance = msg["data"]["utterance"]
                logger.info("Output: " + utterance)
                RemiClient.history_widget.append(
                    "Jarbas: " + utterance.lower())
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


class RemiClient(App):
    protocol = None
    history_widget = None

    def __init__(self, *args):
        super(RemiClient, self).__init__(*args)

    def main(self):
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

        self.suggestions = ["hello world",
                            "do you like pizza",
                            "tell me about nicola tesla",
                            "tell me a joke"]
        self.name = "remi_gui"

        self.reactor_loop = Thread(target=reactor.run)
        self.reactor_loop.setDaemon(True)
        self.reactor_loop.start()

        # returning the root widget
        return self.get_chat_widget()

    def get_chat_widget(self):
        verticalContainer = gui.Widget(width=400, margin='0px auto',
                                       style={'display': 'block',
                                              'overflow': 'hidden'})
        chatButtonContainer = gui.Widget(width=400,
                                         layout_orientation=gui.Widget.LAYOUT_HORIZONTAL,
                                         margin='0px',
                                         style={'display': 'block',
                                                'overflow': 'auto'})

        RemiClient.history_widget = gui.ListView.new_from_list((), width=500,
                                                         height=300,
                                                         margin='10px')

        self.txt_input = gui.TextInput(width=400, height=30, margin='10px')
        self.txt_input.set_text('chat: ')
        self.txt_input.set_on_change_listener(self.on_chat_type)
        self.txt_input.set_on_enter_listener(self.on_chat_enter)

        send_button = gui.Button('Send', width=150, height=30, margin='10px')
        send_button.set_on_click_listener(self.on_chat_click)

        sug_button = gui.Button('Suggestion', width=150, height=30,
                                margin='10px')
        sug_button.set_on_click_listener(self.on_sug_click)

        chatButtonContainer.append(send_button)
        chatButtonContainer.append(sug_button)

        verticalContainer.append(self.txt_input)
        verticalContainer.append(chatButtonContainer)
        verticalContainer.append(RemiClient.history_widget)
        return verticalContainer

    def on_sug_click(self, widget):
        sug = random.choice(self.suggestions)
        self.txt_input.set_text('chat: ' + sug)
        self.utterance = sug

    def on_chat_type(self, widget, newValue):
        self.utterance = str(newValue)

    def on_chat_click(self, widget):
        self.utterance = self.utterance.replace("chat:", "").lower()
        msg = {"data": {"utterances": [self.utterance], "lang": "en-us"},
               "type": "recognizer_loop:utterance",
               "context": {"source": RemiClient.protocol.peer,
                           "destinatary":
                   "https_server", "platform": platform}}
        msg = json.dumps(msg)
        RemiClient.protocol.sendMessage(msg, False)

        RemiClient.history_widget.append("you: " + self.utterance.replace("chat:",
                                                                    "").lower())
        self.txt_input.set_text('chat: ')
        self.utterance = ""

    def on_chat_enter(self, widget, userData):
        self.utterance = userData.replace("chat:", "").lower()

        msg = {"data": {"utterances": [self.utterance], "lang": "en-us"},
               "type": "recognizer_loop:utterance",
               "context": {"source": RemiClient.protocol.peer,
                           "destinatary":
                   "https_server", "platform": platform}}
        msg = json.dumps(msg)
        RemiClient.protocol.sendMessage(msg, False)

        RemiClient.history_widget.append("you: " + self.utterance.replace("chat:",
                                                                    "").lower())
        self.txt_input.set_text('chat: ')
        self.utterance = ""


def start_server(host='127.0.0.1', port=8171):
    start(RemiClient, address=host, port=port, multiple_instance=True,
          enable_file_cache=True, update_interval=0.1, start_browser=False)


def start_standalone():
    start(RemiClient, standalone=True)


if __name__ == "__main__":
    start_standalone()
