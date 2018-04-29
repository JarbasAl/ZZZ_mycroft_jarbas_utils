#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright 2016 Mycroft AI, Inc.
#
# This file is part of Mycroft Core.
#
# Mycroft Core is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Mycroft Core is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
6  # along with Mycroft Core.  If not, see <http://www.gnu.org/licenses/>.

import base64
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import tornado.options
import os
from subprocess import check_output
from os.path import dirname
from twisted.internet import reactor, ssl

from autobahn.twisted.websocket import WebSocketClientFactory, \
    WebSocketClientProtocol
from twisted.internet.protocol import ReconnectingClientFactory

import json
import sys
from threading import Thread

import logging

logger = logging.getLogger("Jarbas_WebChatClient")
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel("INFO")

ip = check_output(['hostname', '--all-ip-addresses']).replace(" \n", "")
clients = {}
lang = "en-us"
platform = "JarbasWebChatClientv0.1"


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html', ip=ip, port=port)


class StaticFileHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('js/app.js')


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    peer = "unknown"
    server = None

    def open(self):
        print('Client IP: ' + self.request.remote_ip)
        self.peer = self.request.remote_ip
        clients[self.peer] = self
        self.write_message("Welcome to Jarbas Web Client")
        self.server.chat = self

    def on_message(self, message):
        utterance = message.strip()
        print("Utterance : " + utterance)
        if utterance:
            if utterance == '"mic_on"':
                pass
            else:
                data = {"utterances": [utterance], "lang": lang}
                context = {"source": self.peer, "destinatary":
                    "skills", "client_name": platform, "peer": self.peer}
                msg = {"data": data,
                       "type": "recognizer_loop:utterance",
                       "context": context}
                msg = json.dumps(msg)
                self.server.sendMessage(msg, False)

    def on_close(self):
        global clients
        clients.pop(self.peer)


class JarbasWebchatClientProtocol(WebSocketClientProtocol):
    chat = None

    def onConnect(self, response):
        logger.info("Server connected: {0}".format(response.peer))

    def onOpen(self):
        logger.info("WebSocket connection open. ")
        self.webchat = Thread(target=self.serve_chat)
        self.webchat.setDaemon(True)
        self.webchat.start()

    def serve_chat(self):
        import tornado.options
        WebSocketHandler.server = self
        config = {"port": 8286}
        port = config.get("port", 8286)
        cert = config.get("cert_file",
                          dirname(dirname(dirname(__file__))) + '/certs/JarbasServer.crt')
        key = config.get("key_file",
                         dirname(dirname(dirname(__file__))) + '/certs/JarbasServer.key')

        tornado.options.parse_command_line()

        routes = [
            tornado.web.url(r"/", MainHandler, name="main"),
            tornado.web.url(r"/static/(.*)", tornado.web.StaticFileHandler, {'path': './'}),
            tornado.web.url(r"/ws", WebSocketHandler)
        ]

        settings = {
            "debug": True,
            "template_path": os.path.join(os.path.dirname(__file__), "templates"),
            "static_path": os.path.join(os.path.dirname(__file__), "static"),
        }

        application = tornado.web.Application(routes, **settings)
        if config.get("ssl", False):
            httpServer = tornado.httpserver.HTTPServer(application, ssl_options={
                "certfile": cert,
                "keyfile": key
            })
            url = "https://" + str(ip) + ":" + str(port)
        else:
            httpServer = tornado.httpserver.HTTPServer(application)
            url = "http://" + str(ip) + ":" + str(port)

        tornado.options.parse_command_line()

        print "*********************************************************"
        print "*   Access from web browser " + url
        print "*********************************************************"

        httpServer.listen(port)
        tornado.ioloop.IOLoop.instance().start()

    def onMessage(self, payload, isBinary):
        if not isBinary:
            msg = json.loads(payload)
            if msg.get("type", "") == "speak":
                utterance = msg["data"]["utterance"]
                logger.info("Output: " + utterance)
                if self.chat is not None:
                    self.chat.write_message(utterance)
            if msg.get("type", "") == "hivemind.complete_intent_failure":
                logger.error("Output: complete_intent_failure")
        else:
            pass

    def onClose(self, wasClean, code, reason):
        logger.info("WebSocket connection closed: {0}".format(reason))


class JarbasWebchatClientFactory(WebSocketClientFactory, ReconnectingClientFactory):
    protocol = JarbasWebchatClientProtocol

    def __init__(self, *args, **kwargs):
        super(JarbasWebchatClientFactory, self).__init__(*args, **kwargs)
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


def start_webchat(host="0.0.0.0", port=5678, name="standalone cli client", api="test_key"):
    authorization = name + ":" + api
    usernamePasswordDecoded = authorization
    api = base64.b64encode(usernamePasswordDecoded)
    headers = {'authorization': api}
    adress = u"wss://" + host + u":" + str(port)
    factory = JarbasWebchatClientFactory(adress, headers=headers,
                                         useragent=platform)
    factory.protocol = JarbasWebchatClientProtocol
    contextFactory = ssl.ClientContextFactory()
    reactor.connectSSL(host, port, factory, contextFactory)
    reactor.run()


if __name__ == '__main__':
    start_webchat()
