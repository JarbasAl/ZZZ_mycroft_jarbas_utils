# Intent Engine Skill

IntentEngine skill is a Mycroft skill baseclass that registers and triggers intents

# features

- edits user configuration to make self a priority skill
- listens for messages to register intents/entities
- [base class]() to implement your own engine
- on fallback trigger uses engine to determine intent
- registers self as a fallback skill, priority configurable

# usage

sample [Padaos](https://github.com/MatthewScholefield/padaos) skill, this is a pointless engine to use in practice, since it is part of padatious

    from mycroft_jarbas_utils.skills.intent_engine import IntentEngineSkill, IntentEngine
    from padaos import IntentContainer
    
    # engine wrapper
    class PadaosEngine(IntentEngine):
        def __init__(self):
            self.name = "Padaos"
            IntentEngine.__init__(self, self.name)
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
            
            
Other skills may register intents using


    def register_padaos_intent(name, samples, handler):
        message = "padaos:register_intent"
        name = str(self.skill_id) + ':' + name
        data = {"name": name, "samples": samples}
                
        self.emitter.emit(Message(message, data))
        self.add_event(name, handler, 'mycroft.skill.handler')
    
    
    def register_padaos_entity(name, samples):
        message = "padaos:register_entity"
        name = str(self.skill_id) + ':' + name
        data = {"name": name, "samples": samples}
        self.emitter.emit(Message(message, data))