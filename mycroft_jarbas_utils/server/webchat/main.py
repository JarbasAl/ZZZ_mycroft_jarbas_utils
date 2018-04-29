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
# along with Mycroft Core.  If not, see <http://www.gnu.org/licenses/>.

from mycroft.util import create_signal
from mycroft.util.log import LOG
from mycroft.configuration import Configuration
from mycroft.messagebus.client.ws import WebsocketClient
from mycroft.messagebus.message import Message
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import tornado.options
import os
from subprocess import check_output
from os.path import dirname

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

    def create_internal_emitter(self):
        # connect to mycroft internal websocket
        self.emitter = WebsocketClient()
        self.register_internal_messages()
        self.emitter_thread = Thread(target=self.connect_to_internal_emitter)
        self.emitter_thread.setDaemon(True)
        self.emitter_thread.start()

    def register_internal_messages(self):
        # catch all messages
        self.emitter.on('speak', self.handle_speak)

    def connect_to_internal_emitter(self):
        self.emitter.run_forever()

    def open(self):
        LOG.info('Client IP: ' + self.request.remote_ip)
        self.peer = self.request.remote_ip
        clients[self.peer] = self
        self.create_internal_emitter()
        self.write_message("Welcome to Jarbas Web Client")

    def on_message(self, message):
        utterance = message.strip()
        LOG.info("Utterance : " + utterance)
        if utterance:
            if utterance == '"mic_on"':
                create_signal('startListening')
            else:
                data = {"utterances": [utterance], "lang": lang}
                context = {"source": self.peer, "destinatary":
                    "skills", "client_name": platform, "peer": self.peer}
                self.emitter.emit(Message("recognizer_loop:utterance", data, context))

    def handle_speak(self, event):
        if event.context.get("client_name", platform) == platform:
            peer = event.context.get("peer", "")
            if peer == self.peer:
                self.write_message(event.data['utterance'])

    def on_close(self):
        global clients
        self.emitter.remove("speak", self.handle_speak)
        clients.pop(self.peer)


if __name__ == '__main__':
    import tornado.options

    config = Configuration.get().get("webchat", {})
    port = config.get("port", 8286)
    ssl = config.get("ssl", True)
    cert = config.get("cert_file",
                      dirname(dirname(__file__)) + '/certs/JarbasServer.crt')
    key = config.get("key_file",
                     dirname(dirname(__file__)) + '/certs/JarbasServer.key')

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
    if ssl:
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
