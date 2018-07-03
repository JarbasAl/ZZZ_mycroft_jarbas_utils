from mycroft_jarbas_utils.skills.intent_engine import IntentEngineSkill, \
    IntentEngine
from mycroft.configuration.config import Configuration
from mycroft.skills.core import MycroftSkill, Message
import random


class UnfitEngine(IntentEngine):
    def __init__(self):
        self.name = "unfit"
        IntentEngine.__init__(self, self.name)
        self.config = Configuration.get().get(self.name, {})

    def calc_intent(self, query):
        """ return best intent for this query  """
        data = {"conf": 0,
                "utterance": query,
                "name": None}

        matches = []
        for intent_name in self.intent_samples:
            samples = self.intent_samples[intent_name]
            if query in samples:
                matches.append(intent_name)

        if len(matches):
            # pick a random one!
            intent_name = random.choice(matches)
            data = {"name": intent_name, "conf": 1 - 0.05 * len(matches)}

        entities = []
        for entity in self.entity_samples:
            samples = self.entity_samples
            for s in samples:
                if s in query:
                    entities.append((entity, s))

        data["entities"] = [{entity: s} for entity, s in entities]
        return data


# engine skill for mycroft
class UnfitEngineSkill(IntentEngineSkill):
    def initialize(self):
        priority = 6
        engine = UnfitEngine()
        self.bind_engine(engine, priority)


class UnfitSkill(MycroftSkill):
    def register_unfit_intent(self, name, samples, handler):
        message = "unfit:register_intent"
        name = str(self.skill_id) + ':' + name
        data = {"name": name, "samples": samples}

        self.emitter.emit(Message(message, data))
        self.add_event(name, handler, 'mycroft.skill.handler')

    def register_unfit_entity(self, name, samples):
        message = "unfit:register_entity"
        name = str(self.skill_id) + ':' + name
        data = {"name": name, "samples": samples}
        self.emitter.emit(Message(message, data))


def create_skill():
    return UnfitEngineSkill()
