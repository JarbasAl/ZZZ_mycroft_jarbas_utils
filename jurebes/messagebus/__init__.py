from mycroft.messagebus.message import Message
from mycroft.util.log import LOG
from mycroft.configuration import Configuration
from mycroft.messagebus.client.ws import WebsocketClient
from threading import Thread
import time

__author__ = "jarbas"


class BusQuery(object):
    def __init__(self, emitter, message_type, message_data=None,
                 message_context=None):
        self.emitter = emitter
        self.waiting = False
        self.response = Message(None, None, None)
        self.query_type = message_type
        self.query_data = message_data
        self.query_context = message_context
        self.events = []

    def add_response_type(self, response_type):
        self.emitter.on(response_type, self._end_wait)
        self.events.append(response_type)

    def _end_wait(self, message):
        self.response = message
        self.waiting = False

    def _wait_response(self, timeout):
        start = time.time()
        elapsed = 0
        self.waiting = True
        while self.waiting and elapsed < timeout:
            elapsed = time.time() - start
            time.sleep(0.1)
        self.waiting = False

    def send(self, response_type=None, timeout=10):
        self.response = Message(None, None, None)
        if response_type is None:
            response_type = self.query_type + ".reply"
        self.emitter.on(response_type, self._end_wait)
        self.events.append(response_type)
        self.emitter.emit(
            Message(self.query_type, self.query_data, self.query_context))
        self._wait_response(timeout)
        return self.response.data

    def get_response_type(self):
        return self.response.type

    def get_response_data(self):
        return self.response.data

    def get_response_context(self):
        return self.response.context

    def remove_listeners(self):
        for event in self.events:
            self.emitter.remove(event, self._end_wait)

    def shutdown(self):
        """ remove all listeners """
        self.remove_listeners()


class BusResponder(object):
    def __init__(self, emitter, response_type, response_data=None,
                 response_context=None, trigger_messages=None):
        self.emitter = emitter
        self.response_type = response_type
        self.response_data = response_data
        self.response_context = response_context
        trigger_messages = trigger_messages or []
        self.events = []
        for message_type in trigger_messages:
            self.listen(message_type)

    def listen(self, message_type, callback=None):
        if callback is None:
            callback = self._respond
        self.emitter.on(message_type, callback)
        self.events.append((message_type, callback))

    def update_response(self, data=None, context=None):
        if data is not None:
            self.response_data = data
        if context is not None:
            self.response_context = context

    def _respond(self, message):
        self.emitter.emit(message.reply(self.response_type,
                                        self.response_data,
                                        self.response_context))

    def shutdown(self):
        """ remove all listeners """
        for event, callback in self.events:
            self.emitter.remove(event, callback)


class ResponderBackend(object):
    """
        Base class for all responder implementations.


        set response handlers for specific message_types

    """

    def __init__(self, name=None, emitter=None, logger=None):
        """
           initialize responder

           args:
                name(str): name identifier
                emitter (WebsocketClient): mycroft messagebus websocket
                logger (logger) : custom logger if desired
        """
        if name is None:
            self.name = "ResponderBackend"
        else:
            self.name = name
        if emitter is None:
            self.emitter = WebsocketClient()

            def connect():
                self.emitter.run_forever()
            ws_thread = Thread(target=connect)
            ws_thread.setDaemon(True)
            ws_thread.start()
        else:
            self.emitter = emitter
        self.response_type = "default.reply"
        if self.responder:
            self.responder.shutdown()
            self.responder = None
        self.callback = None
        if logger is None:
            self.logger = LOG
        else:
            self.logger = logger
        self.config = Configuration.get().get(self.name, {})
        self.events = []

    def update_response_data(self, response_data=None, response_context=None):
        """
        change the data of the response to be sent when queried

        Args:
                message_data (dict): response message data
                message_context (dict): response message context

        """
        if self.responder is not None:
            self.responder.update_response(response_data, response_context)

    def set_response_handler(self, trigger_message, callback, response_data=None,
                             response_context=None):
        """
          prepare responder for sending, register answers

          args:
                trigger_message (str): message_type that triggers response
                callback (function): to execute on message_type
                response_data (dict) : default data of the response message
                response_context (dict) : default context of the response message
        """

        # update message context
        response_context = response_context or {}
        response_context["source"] = self.name
        response_context["triggered_by"] = trigger_message

        # generate reply message
        if ".request" in trigger_message:
            self.response_type = trigger_message.replace(".request", ".reply")
        else:
            self.response_type = trigger_message + ".reply"

        self.responder = BusResponder(self.emitter, self.response_type,
                                      response_data, response_context,
                                      [])
        self.callback = callback
        self.emitter.on(trigger_message, self._respond)
        self.events.append(trigger_message)

    def _respond(self, message):
        """
          on query execute callback and send a response

          args:
                message (Message) : query message
        """
        try:
            if self.callback:
                self.callback(message)
        except Exception as e:
            self.logger.error(e)
        self.responder.respond(message)

    def shutdown(self):
        """ remove all listeners """
        for event in self.events:
            self.emitter.remove(event, self._respond)

        if self.responder:
            self.responder.shutdown()
            self.responder = None


class QueryBackend(object):
    """
        Base class for all query implementations. waits timeout seconds for
        answer, considered answers are generated as follows

            query:
                deep.dream.request
                deep.dream
            possible responses:
                deep.dream.reply,
                deep.dream.result,
                deep.dream.response

            query:
                face.recognition.request
                face.recognition
            possible responses:
                 face.recognition.reply,
                 face.recognition.result,
                 face.recognition.response

    """

    def __init__(self, name=None, emitter=None, timeout=5, logger=None):
        """
           initialize emitter, register events, initialize internal variables

           args:
                name(str): name identifier
                emitter (WebsocketClient): mycroft messagebus websocket
                timeout (int): maximum seconds to wait for reply
                logger (logger) : custom logger if desired
        """
        if name is None:
            self.name = "QueryBackend"
        else:
            self.name = name
        if emitter is None:
            self.emitter = WebsocketClient()

            def connect():
                self.emitter.run_forever()

            ws_thread = Thread(target=connect)
            ws_thread.setDaemon(True)
            ws_thread.start()
        else:
            self.emitter = emitter
        self.timeout = timeout
        self.query = None
        if logger is None:
            self.logger = LOG
        else:
            self.logger = logger
        self.waiting_messages = []
        self.elapsed_time = 0
        self.config = Configuration.get().get(self.name, {})
        self.result = {}

    def send_request(self, message_type, message_data=None,
                     message_context=None, response_messages=None):
        """
          prepare query for sending, add several possible kinds of
          response message automatically
                "message_type.reply" ,
                "message_type.response",
                "message_type.result"

        args:
                message_type (str): query message type
                message_data (dict): query message data
                message_context (dict): query message context
                response_messages (list) : list of extra messages to end wait
        """
        if response_messages is None:
            response_messages = []
        # generate reply messages
        self.waiting_messages = response_messages
        if ".request" in message_type:
            response = message_type.replace(".request", ".reply")
            if response not in self.waiting_messages:
                self.waiting_messages.append(response)
            response = message_type.replace(".request", ".response")
            if response not in self.waiting_messages:
                self.waiting_messages.append(response)
            response = message_type.replace(".request", ".result")
            if response not in self.waiting_messages:
                self.waiting_messages.append(response)
        else:
            response = message_type + ".reply"
            if response not in self.waiting_messages:
                self.waiting_messages.append(response)
            response = message_type + ".response"
            if response not in self.waiting_messages:
                self.waiting_messages.append(response)
            response = message_type + ".result"
            if response not in self.waiting_messages:
                self.waiting_messages.append(response)

        # update message context
        if message_context is None:
            message_context = {}
        message_context["source"] = self.name
        message_context["waiting_for"] = self.waiting_messages
        start = time.time()
        self.elapsed_time = 0
        result = self._send_internal_request(message_type, message_data,
                                                   message_context)
        self.elapsed_time = time.time() - start
        return result

    def _send_internal_request(self, message_type, message_data,
                               message_context):
        """
        send query to messagebus

             Args:
                message_type (str): query message type
                message_data (dict): query message data
                message_context (dict): query message context
        """
        self.query = BusQuery(self.emitter, message_type, message_data,
                              message_context)
        for message in self.waiting_messages[1:]:
            self.query.add_response_type(message)
        return self.query.send(self.waiting_messages[0], self.timeout)

    def get_result(self, context=False, type=False):
        """
            return last processed response message data


             Args:
                type (bool): return response message type
                context (bool): return response message context

        """
        if self.query is None:
            return None
        if type:
            return self.query.get_response_type()
        if context:
            return self.query.get_response_context()
        return self.query.get_response_data()

    def shutdown(self):
        """ remove all listeners """
        if self.query:
            self.query.shutdown()