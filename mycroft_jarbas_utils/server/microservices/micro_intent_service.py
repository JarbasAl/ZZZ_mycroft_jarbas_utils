from mycroft.skills.intent_service import IntentService, normalize, LOG, open_intent_envelope


class MicroIntentService(IntentService):

    def __init__(self, ws):
        self.intent_map = {}
        self.skills_map = {}
        self.vocab_map = {}
        IntentService.__init__(self, ws)
        self.emitter.on("skill.loaded", self.handle_skill_load)
        self.emitter.on("skill.shutdown", self.handle_skill_shutdown)

    def handle_utterance(self, message):
        pass

    def handle_register_vocab(self, message):
        start_concept = message.data.get('start')
        end_concept = message.data.get('end')
        regex_str = message.data.get('regex')
        alias_of = message.data.get('alias_of')
        if regex_str:
            self.engine.register_regex_entity(regex_str)
        else:
            if start_concept:
                self.vocab_map[start_concept] = end_concept
            self.engine.register_entity(
                start_concept, end_concept, alias_of=alias_of)

    def handle_register_intent(self, message):
        intent = open_intent_envelope(message)
        self.engine.register_intent_parser(intent)
        skill_id, intent = message.data.get("name", "None:None").split(":")
        LOG.info("Registered: " + intent)
        if skill_id not in self.intent_map.keys():
            self.intent_map[skill_id] = []
        self.intent_map[skill_id].append(intent)

    def handle_detach_intent(self, message):
        intent_name = message.data.get('intent_name')
        new_parsers = [
            p for p in self.engine.intent_parsers if p.name != intent_name]
        self.engine.intent_parsers = new_parsers
        skill_id, intent = intent_name.split(":")
        self.intent_map[skill_id].pop(intent)

    def handle_detach_skill(self, message):
        skill_id = message.data.get('skill_id')
        new_parsers = [
            p for p in self.engine.intent_parsers if
            not p.name.startswith(skill_id)]
        self.engine.intent_parsers = new_parsers
        self.intent_map.pop(skill_id)

    def handle_skill_shutdown(self, message):
        name = message.data.get("name")
        id = message.data.get("id")
        self.skills_map[id] = name

    def handle_skill_load(self, message):
        id = message.data.get("id")
        self.skills_map.pop(id)

    def get_skills_map(self, lang="en-us"):
        return self.skills_map

    def get_intent_map(self, lang="en-us"):
        return self.intent_map

    def get_vocab_map(self, lang="en-us"):
        return self.vocab_map

    def get_intent(self, utterance, lang="en-us"):
        best_intent = None
        try:
            # normalize() changes "it's a boy" to "it is boy", etc.
            best_intent = next(self.engine.determine_intent(
                normalize(utterance, lang), 100,
                include_tags=True,
                context_manager=self.context_manager))
            # TODO - Should Adapt handle this?
            best_intent['utterance'] = utterance
        except Exception as e:
            LOG.exception(e)

        if best_intent and best_intent.get('confidence', 0.0) > 0.0:
            return best_intent
        else:
            return None
