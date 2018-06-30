from mycroft.configuration import Configuration


class IntentEngine(object):
    def __init__(self, name):
        self.name = name
        self.config = Configuration.get().get(name, {})
        self.intent_samples = {}
        self.entity_samples = {}

    def add_intent(self, name, samples):
        self.intent_samples[name] = samples

    def remove_intent(self, name):
        if name in self.intent_samples:
            del self.intent_samples[name]

    def add_entity(self, name, samples):
        self.entity_samples[name] = samples

    def remove_entity(self, name):
        if name in self.entity_samples:
            del self.entity_samples[name]

    def train(self, single_thread=False):
        """ train all registered intents and entities"""
        pass

    def calc_intent(self, query):
        """ return best intent for this query  """
        data = {"conf": 0,
                "utterance": query,
                "name": None}
        return data
