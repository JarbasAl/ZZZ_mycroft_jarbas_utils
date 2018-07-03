class IntentTestBuilder(object):
    def __init__(self, utterance=None):
        self.reset_builder()
        self.utterance = utterance
        self.tests = []

    def reset_builder(self):
        self.utterance = None
        self.rm_contexts = []
        self.changed_contexts = []
        self.set_contexts = {}
        self.intent_type = None
        self.keywords = {}
        self.expected_response = ""
        self.expected_dialog = ""
        self.expected_data = {}
        self.evaluation_timeout = 30

    def test_utterance(self, utterance):
        """ The text to send to the skill, like it was a spoken command """
        self.utterance = utterance

    def remove_context(self, context_name):
        """ A list of contexts to remove before sending the utterance """
        if context_name not in self.rm_contexts:
            self.rm_contexts.append(context_name)

    def set_context(self, context, data=None):
        """ A list of contexts and corresponding strings to set before sending the utterance """
        if context not in self.set_contexts:
            self.set_contexts[context] = data

    def check_intent(self, intent_type):
        """ Assert that this intent name, as defined in the skills __init__.py code, is used """
        self.intent_type = intent_type

    def check_keyword(self, keyword, value):
        """ test if data from message that triggers intent
        contains keyword with value """
        self.keywords[keyword] = value

    def check_response(self, expected_response):
        """ Assert that the skill speaks a response that matches this regular expression """
        pass

    def check_dialog_file(self, dialog):
        """ Assert that the skill responds with a response from a certain dialog file """
        self.expected_dialog = dialog.replace(".dialog", "")

    def check_data(self, key, value):
        """ test if data from message that triggers intent
                contains key with value """
        self.expected_data[key] = value

    def set_timeout(self, seconds=30):
        """ The default timeout is 30 seconds. If a skill takes longer than this to finish, the evaluation_timeout can be set """
        self.evaluation_timeout = seconds

    def check_changed_context(self, context):
        """ Assert that a list of contexts was set or removed """
        if not isinstance(context, list):
            context = [context]
        for c in context:
            if c not in self.changed_contexts:
                self.changed_contexts.append(c)

    def _build_test(self):
        if self.utterance is None:
            raise NotImplementedError("You need an utterance for testing!")
        if self.intent_type is None:
            raise NotImplementedError("You need to test for an intent!")
        test = {
            "utterance": self.utterance,
            "remove_context": self.rm_contexts,
            "set_context": self.set_contexts,
            "intent_type": self.intent_type,
            "intent": self.keywords,
            "evaluation_timeout": self.evaluation_timeout,
            "changed_context": self.changed_contexts

        }
        if self.expected_response:
            test["expected_response"] = self.expected_response
        if self.expected_data:
            test["expected_data"] = self.expected_data
        if self.expected_dialog:
            test["expected_dialog"] = self.expected_dialog
        return test

    def build_test(self):
        test = self._build_test()
        self.tests.append(test)
        self.reset_builder()
        return test

    def get_all_tests(self):
        return self.tests
