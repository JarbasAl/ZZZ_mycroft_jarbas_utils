from mycroft.skills.core import MycroftSkill, FallbackSkill
from mycroft.skills.skill_data import munge_intent_parser
from mycroft.skills.audioservice import AudioService


class MutableAudioService(AudioService):
    def __init__(self, emitter):
        super(MutableAudioService, self).__init__(emitter)
        self.events = []
        self.backend = ""

    def register_backend_update(self, intent_name):
        self.emitter.on(intent_name, self.handle_backend_update)
        self.events.append((intent_name, self.handle_backend_update))

    def handle_backend_update(self, message):
        self.backend = message.data.get("AudioBackend", "")

    def play(self, tracks=None, utterance=''):
        utterance = utterance or self.backend
        super(MutableAudioService, self).play(tracks, utterance)

    def shutdown(self):
        self.emitter.remove('mycroft.audio.service.track_info_reply',
                        self._track_info)
        for event, handler in self.events:
            self.emitter.remove(event, handler)


class AudioSkill(MycroftSkill):
    """ Skill that automatically initializes audio service and selects audio
    backend """

    def __init__(self, name=None, emitter=None):
        super(AudioSkill, self).__init__(name, emitter)
        self.audio = None
        self.backends = []

    def bind(self, emitter):
        super(AudioSkill, self).bind(emitter)
        self.init_audio()

    def init_audio(self):
        self.audio = MutableAudioService(self.emitter)
        self.backends = self.config_core \
            .get("Audio", {}) \
            .get("backends", {}) \
            .keys()
        for backend in self.backends:
            modifiers = [" in ", " on ", " at ", " from "]
            for backend in self.backends:
                for m in modifiers:
                    self.register_vocabulary(m + backend, "AudioBackend")
            self.register_vocabulary(backend, "AudioBackend")

    def register_intent(self, intent_parser, handler, need_self=False):
        name = intent_parser.name or handler.__name__
        munge_intent_parser(intent_parser, name, self.skill_id)
        self.audio.register_backend_update(intent_parser.name)
        super(AudioSkill, self).register_intent(intent_parser
                                                .optionally("AudioBackend"),
                                                handler, need_self)

    def shutdown(self):
        super(AudioSkill, self).shutdown()
        self.audio.shutdown()


class AudioFallback(AudioSkill, FallbackSkill):
    """
    FallbackSkill that automatically initializes audio service and
    selects audio backend
    """

    def __init__(self, name=None, emitter=None):
        super(AudioFallback, self).__init__(name, emitter)
