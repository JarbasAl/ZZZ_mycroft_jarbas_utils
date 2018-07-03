# IntentEngine

base class to add new intent engines to mycroft

# usage

    class MyEngine(IntentEngine):
    def __init__(self):
        self.name = "MyEngine"
        IntentEngine.__init__(self, self.name)


    def train(self, single_thread=False):
        """ train all registered intents and entities"""
        
        for intent_name in self.intent_samples:
            samples = self.intent_samples[name]
            # implement your training here
        

    def calc_intent(self, query):
        """ return best intent for this query  """
        data = {"conf": 0,
                "utterance": query,
                "name": None}
        # calculate the intent here
        return data
