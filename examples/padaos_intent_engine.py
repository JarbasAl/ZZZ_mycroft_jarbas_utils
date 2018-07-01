from mycroft_jarbas_utils.skills.intent_engine import IntentEngineSkill, \
    IntentEngine
from mycroft.configuration.config import Configuration

from padaos import IntentContainer


class PadaosEngine(IntentEngine):
    def __init__(self):
        self.name = "Padaos"
        IntentEngine.__init__(self, self.name)
        self.config = Configuration.get().get(self.name, {})
        self.container = IntentContainer()

    def add_intent(self, name, samples):
        self.container.add_intent(name, samples)

    def remove_intent(self, name):
        self.container.remove_intent(name)

    def add_entity(self, name, samples):
        self.container.add_entity(name, samples)

    def remove_entity(self, name):
        self.container.remove_entity(name)

    def train(self, single_thread=False):
        """ train all registered intents and entities"""
        # Padaos is simply regex, it handles this when registering
        pass

    def calc_intent(self, query):
        """ return best intent for this query  """
        data = {"conf": 0,
                "utterance": query,
                "name": None}
        data.update(self.container.calc_intent(query))
        return data


# engine skill for mycroft
class PadaosSkill(IntentEngineSkill):
    def initialize(self):
        priority = 4
        engine = PadaosEngine()
        self.bind_engine(engine, priority)


def create_skill():
    return PadaosSkill()
