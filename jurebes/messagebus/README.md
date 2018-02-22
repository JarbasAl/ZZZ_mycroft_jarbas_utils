# JUREBES-messagebus
# BusQuery

Sends a message.type to the messagebus and waits for the reply

    from jurebes.messagebus import BusQuery

    def initialize(self):
        # set query data
        query_type = "my_message.request"
        query_data = {"url":"http://link.com"}
        query_context = {"source": "my awesome skill"}
        self.query = BusQuery(self.emitter, query_type, query_data,
                     query_context)

        # set query response message
        response_type = "my_message.reply"
        self.query.add_response_type(response_type)

    def my_intent(self, message):
        # send query for data from other skill
        data = self.query.send(timeout=10) # wait maximum 10 seconds for answer

    def my_other_method(self):
        # get info from the reply manually, example if timeout=0 and doing async stuff
        type = self.query.get_response_type()
        data = self.query.get_response_data()
        context = self.query.get_response_context()


# BusResponder

Emit a message automatically on message_type

    from jurebes.messagebus import BusResponder

    def initialize(self):
        response_type = "my_message.reply"
        responde_data = {"result": {}}
        responde_context = {"source": "my awesome skill"}
        trigger_messages = ["my_message"]
        self.responder = BusResponder(self.emitter, response_type,response_data,
                     response_context, trigger_messages)


In addition two support tools were made that use this internally

# BusQueryBackend

This is template class, meant to be overrided the following way

    from jurebes.messagebus import QueryBackend

    class RBMQuery(QueryBackend):
        def __init__(self, name=None, emitter=None, timeout=35, logger=None):
            super(RBMQuery, self).__init__(name=name, emitter=emitter,
                                           timeout=timeout, logger=logger)

        def sample(self, model="random", sample_num=3, context=None):
            result = self.send_request("RBM.request",
                                     {"model": model, "sample_num":sample_num},
                                     message_context=context)
            result = result.get("samples")
            return result

Then the overrided class is imported to use the functionality from anywhere, this will synchronize both skills until an answer is received

# BusResponderBackend

This allows a skill to add a response handler that is triggered on certain message types, the callback function then updates the response data at the end and the reply is transmitted

    from jurebes.messagebus import ResponderBackend

    def initialize(self):
        self.responder = ResponderBackend(self.name, self.emitter, self.log)
        self.responder.set_response_handler("listen.for.this.message.type", self.handle_this message)

    def handle_this_message(self, message):
        # do things
        # update responder answer
            # context = {} # message object context field
            # data = {} # message data field
            self.responder.update_response_data(data, context)

