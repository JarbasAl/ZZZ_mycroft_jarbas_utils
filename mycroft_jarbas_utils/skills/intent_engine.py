from threading import Event
from time import time as get_time, sleep

from mycroft_jarbas_utils.intent.engines import IntentEngine
from mycroft.skills.core import FallbackSkill
from mycroft.util.log import LOG
from mycroft.configuration.config import LocalConf, USER_CONFIG, Configuration
from mycroft.messagebus.message import Message


class IntentEngineSkill(FallbackSkill):
    def __init__(self):
        FallbackSkill.__init__(self)
        self.engine = None
        self.config = {}
        self.priority = 4

    def initialize(self):
        priority = 4
        engine = IntentEngine("dummy")
        self.bind_engine(engine, priority)

    def bind_engine(self, engine, priority=4):
        conf = LocalConf(USER_CONFIG)
        priority_skills = Configuration.get().get("skills", {}).get(
            "priority_skills", [])
        priority_skills.append(self._dir.split("/")[-1])
        conf.store()
        self.priority = priority
        self.engine = engine
        self.config = engine.config
        self.register_messages(engine.name)
        self.register_fallback(self.handle_fallback, self.priority)
        self.finished_training_event = Event()
        self.finished_initial_train = False
        self.train_delay = self.config.get('train_delay', 4)
        self.train_time = get_time() + self.train_delay

    def register_messages(self, name):
        self.emitter.on('mycroft.skills.initialized', self.train)
        self.emitter.on(name + ':register_intent', self._register_intent)
        self.emitter.on(name + ':register_entity', self._register_entity)

    def train(self, message=None):
        single_thread = message.data.get('single_thread', False)
        self.finished_training_event.clear()

        LOG.info('Training...')
        self.engine.train(single_thread=single_thread)
        LOG.info('Training complete.')

        self.finished_training_event.set()
        self.finished_initial_train = True

    def wait_and_train(self):
        if not self.finished_initial_train:
            return
        sleep(self.train_delay)
        if self.train_time < 0.0:
            return

        if self.train_time <= get_time() + 0.01:
            self.train_time = -1.0
            self.train()

    def _register_object(self, message, object_name, register_func):
        name = message.data['name']
        samples = message.data['samples']

        LOG.debug(
            'Registering ' + self.engine.name + ' ' + object_name + ': ' + name)

        register_func(name, samples)
        self.train_time = get_time() + self.train_delay
        self.wait_and_train()

    def register_intent(self, name, samples):
        data = {"name": name, "samples": samples}
        self._register_intent(Message(name, data))

    def register_entity(self, name, samples):
        data = {"name": name, "samples": samples}
        self._register_entity(Message(name, data))

    def _register_intent(self, message):
        self._register_object(message, 'intent', self.engine.add_intent)

    def _register_entity(self, message):
        self._register_object(message, 'entity', self.engine.add_entity)

    def handle_fallback(self, message):
        utt = message.data.get('utterance')
        LOG.debug(self.engine.name + " fallback attempt: " + utt)

        if not self.finished_training_event.is_set():
            LOG.debug('Waiting for training to finish...')
            self.finished_training_event.wait()

        data = self.engine.calc_intent(utt)

        if data["conf"] < 0.5:
            return False

        self.make_active()

        self.emitter.emit(message.reply(data["name"], data=data))
        return True
