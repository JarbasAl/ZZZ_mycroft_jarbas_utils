from mycroft.messagebus.message import Message
from mycroft.version import CORE_VERSION_BUILD
import time

__author__ = "jarbas"


# TODO get vocab,
# TODO munged skill id

class IntentParser(object):
    def __init__(self, emitter, time_out=5, override=False):
        # TODO change this number to version that gets PR merged
        if CORE_VERSION_BUILD < 999 and not override:
            raise NotImplementedError(
                "PR#1351 not in " + str(CORE_VERSION_BUILD))
                # you can manually merge PR and pass override=True
        self.emitter = emitter
        self.time_out = time_out
        self.waiting = False
        self.skills_map = {}
        self.intent_map = {}
        self.intent_data = {}
        self.emitter.on("mycroft.intent.manifest.response",
                        self._handle_receive_intents)
        self.emitter.on("mycroft.skills.manifest.response",
                        self._handle_receive_skills)
        self.emitter.on("mycroft.intent.response",
                        self._handle_receive_intent)
        self.emitter.emit(Message("mycroft.skills.manifest"))
        self.emitter.emit(Message("mycroft.intent.manifest"))

    def get_skill_manifest(self):
        self.update_skill_manifest()
        return self.skills_map

    def get_intent_manifest(self):
        self.update_intent_manifest()
        return self.intent_map

    def determine_intent(self, utterance, lang="en-us"):
        self.waiting = True
        self.emitter.emit(Message("mycroft.intent.get", {"utterance": utterance, "lang": lang}))
        start_time = time.time()
        t = 0
        while self.waiting and t < self.time_out:
            t = time.time() - start_time
        if self.waiting or self.intent_data is None:
            return None, None
        id, intent = self.intent_data["type"].split(":")
        return intent, id

    def update_intent_manifest(self):
        # update skill manifest
        self.waiting = True
        self.id = 0
        self.emitter.emit(Message("mycroft.intent.manifest"))
        start_time = time.time()
        t = 0
        while self.waiting and t < self.time_out:
            t = time.time() - start_time
        if self.waiting:
            self.waiting = False
            return False
        return True

    def update_skill_manifest(self):
        # update skill manifest
        self.waiting = True
        self.id = 0
        self.emitter.emit(Message("mycroft.skills.manifest"))
        start_time = time.time()
        t = 0
        while self.waiting and t < self.time_out:
            t = time.time() - start_time
        if self.waiting:
            self.waiting = False
            return False
        return True

    def get_skill_id(self, intent_name):
        self.update_intent_manifest()
        for skill_id in self.intent_map:
            intents = self.intent_map[skill_id]
            if intent_name in intents:
                return skill_id
        return None

    def _handle_receive_intent(self, message):
        self.intent_data = message.data.get("intent_data", {})
        self.waiting = False

    def _handle_receive_intents(self, message):
        self.intent_map = message.data
        self.waiting = False

    def _handle_receive_skills(self, message):
        self.skills_map = message.data
        self.waiting = False

