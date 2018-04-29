from twisted.internet import reactor, ssl

from autobahn.twisted.websocket import WebSocketClientFactory, \
    WebSocketClientProtocol
from twisted.internet.protocol import ReconnectingClientFactory

import json
import sys
from threading import Thread
import base64
import logging

logger = logging.getLogger("Jarbas_Twitch_Bridge")
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel("INFO")

platform = "JarbasTwitchClientv0.1"

import socket, string


class JarbasTwitchClientProtocol(WebSocketClientProtocol):
    # Set all the variables necessary to connect to Twitch IRC
    HOST = "irc.twitch.tv"
    NICK = "jarbasai"
    PORT = 6667
    PASS = "oauth:qegggytjyjfgdhg"
    CHANNELNAME = "jarbasai"

    def onConnect(self, response):
        logger.info("Server connected: {0}".format(response.peer))

    def onOpen(self):
        logger.info("WebSocket connection open. ")
        self.connect_to_twitch()
        self.HOST = self.factory.host
        self.NICK = self.factory.nick
        self.PORT = self.factory.port
        self.PASS = self.factory.oauth
        self.CHANNELNAME = self.factory.channel
        self.factory.client = self
        self.input_loop = Thread(target=self.twitch_loop)
        self.input_loop.setDaemon(True)
        self.input_loop.start()

    def connect_to_twitch(self):
        # Connecting to Twitch IRC by passing credentials and joining a certain channel
        self.s = socket.socket()
        self.s.connect((self.HOST, self.PORT))
        self.s.send("PASS " + self.PASS + "\r\n")
        self.s.send("NICK " + self.NICK + "\r\n")
        self.s.send("JOIN #" + self.CHANNELNAME + " \r\n")

    # Method for sending a message
    def twitch_send(self, message):
        self.s.send("PRIVMSG #" + self.CHANNELNAME + " :" + message + "\r\n")

    def onMessage(self, payload, isBinary):
        if not isBinary:
            msg = json.loads(payload)
            if msg.get("type", "") == "speak":
                utterance = msg["data"]["utterance"]
                user = msg.get("context", {}).get("user")
                logger.info("Output: " + utterance)
                if user:
                    utterance += " " + user
                self.twitch_send(utterance)
            if msg.get("type", "") == "hivemind.complete_intent_failure":
                logger.error("Output: complete_intent_failure")
                self.twitch_send("does not compute")
        else:
            pass

    def onClose(self, wasClean, code, reason):
        logger.info("WebSocket connection closed: {0}".format(reason))

    def twitch_loop(self):

        readbuffer = ""
        MODT = False

        while True:
            readbuffer = readbuffer + self.s.recv(1024)
            temp = string.split(readbuffer, "\n")
            readbuffer = temp.pop()

            for line in temp:
                # Checks whether the message is PING because its a method of Twitch to check if you're afk
                if (line[0] == "PING"):
                    self.s.send("PONG %s\r\n" % line[1])
                else:
                    # Splits the given string so we can work with it better
                    parts = string.split(line, ":")

                    if "QUIT" not in parts[1] and "JOIN" not in parts[1] and "PART" not in parts[1]:
                        try:
                            # Sets the message variable to the actual message sent
                            message = parts[2][:len(parts[2]) - 1]
                        except:
                            message = ""
                        # Sets the username variable to the actual username
                        usernamesplit = string.split(parts[1], "!")
                        username = usernamesplit[0]
                        print message
                        if "@" + self.NICK in message:
                            message = message.replace("@" + self.NICK, "")
                            # Only works after twitch is done announcing stuff (MODT = Message of the day)
                            if MODT:
                                msg = {"data": {"utterances": [message], "lang": "en-us"},
                                       "type": "recognizer_loop:utterance",
                                       "context": {"source": "twitch", "destinatary":
                                           "https_server", "platform": platform, "user": username}}
                                msg = json.dumps(msg)
                                self.sendMessage(msg, False)

                        for l in parts:
                            if "End of /NAMES list" in l:
                                MODT = True


class JarbasTwitchClientFactory(WebSocketClientFactory, ReconnectingClientFactory):
    protocol = JarbasTwitchClientProtocol

    def __init__(self, nick, oauth, channel, host="irc.twitch.tv", port=6667, *args, **kwargs):
        super(JarbasTwitchClientFactory, self).__init__(*args, **kwargs)
        self.status = "disconnected"
        self.client = None
        self.factory.host = host
        self.factory.nick = nick
        self.factory.port = port
        self.factory.oauth = oauth
        self.factory.channel = channel

    # websocket handlers
    def clientConnectionFailed(self, connector, reason):
        logger.info("Client connection failed: " + str(reason) + " .. retrying ..")
        self.status = "disconnected"
        self.retry(connector)

    def clientConnectionLost(self, connector, reason):
        logger.info("Client connection lost: " + str(reason) + " .. retrying ..")
        self.status = "disconnected"
        self.retry(connector)


def run_twitch(oauth, nick="JarbasAI", channel="jarbasai", host="127.0.0.1",
               port=5678, name="jarbas twitch bridge", api="test_key"):
    authorization = name + ":" + api
    usernamePasswordDecoded = authorization
    api = base64.b64encode(usernamePasswordDecoded)
    headers = {'authorization': api}
    adress = u"wss://" + host + u":" + str(port)
    factory = JarbasTwitchClientFactory(adress, oauth=oauth, nick=nick, channel=channel,
                                        headers=headers, useragent=platform)
    factory.protocol = JarbasTwitchClientProtocol
    contextFactory = ssl.ClientContextFactory()
    reactor.connectSSL(host, port, factory, contextFactory)
    reactor.run()
