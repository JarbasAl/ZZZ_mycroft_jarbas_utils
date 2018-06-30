import unittest
from mycroft_jarbas_utils.skills.auto_translatable import AutotranslatableSkill
from mycroft.messagebus.message import Message


class MockEmitter(object):
    def __init__(self):
        self.reset()

    def emit(self, message):
        self.types.append(message.type)
        self.results.append(message.data)

    def get_types(self):
        return self.types

    def get_results(self):
        return self.results

    def on(self, event, f):
        pass

    def reset(self):
        self.types = []
        self.results = []


class AutoTranslateSkillTest(unittest.TestCase):
    emitter = MockEmitter()

    def setUp(self):
        self.emitter.reset()

    def test_lang_detect(self):
        skill = _TestSkill()
        skill.bind(self.emitter)
        skill.initialize()
        # TODO find other package, sometimes it say nl instead of en
        # self.assertEqual(skill.language_detect("hello world"), "en")
        self.assertEqual(skill.language_detect("my name is mycroft"), "en")
        self.assertEqual(skill.language_detect("olá mundo"), "pt")

    def test_translate_string(self):
        skill = _TestSkill()
        skill.bind(self.emitter)
        skill.initialize()
        self.assertEqual(skill.translate("hello world", "pt").lower(),
                         "olá mundo")
        self.assertEqual(skill.translate("Olá Mundo", "en").lower(),
                         "hello world")

    def test_translate_utterance(self):
        skill = _TestSkill()
        skill.bind(self.emitter)
        skill.initialize()
        self.assertEqual(
            skill._translate_utterance("my name is mycroft", "pt").lower(),
            "meu nome é mycroft")
        self.assertEqual(skill._translate_utterance("my name is mycroft", "pt",
                                                    {"user": "test"}),
                         ('meu nome é mycroft', {'auto_translated': True,
                                                 'original_utterance': 'my name is mycroft',
                                                 'source_lang': 'en',
                                                 'target_lang': 'pt',
                                                 'user': 'test'})
                         )

    def test_call_translate_message(self):
        skill = SimpleSkill2()
        skill.bind(self.emitter)
        skill.initialize()
        self.assertEqual(skill.message_tx_called, False)
        self.assertEqual(skill.handler_called, False)
        skill.call_intent()
        self.assertEqual(skill.message_tx_called, True)
        self.assertEqual(skill.handler_called, True)

    # TODO find why it is failing
    def test_translate_message(self):
        skill = SimpleSkill1()
        skill.bind(self.emitter)
        skill.initialize()
        message = Message("test.message",
                          {"utterance": "meu nome é mycroft"})
        tx = skill._translate_message(message)
        self.assertEqual(tx.type, "test.message")
        self.assertEqual(tx.data, {"utterance": "my name is mycroft"})

        message = Message("test.message2",
                          {"book": "eu gosto de ler livros"})
        tx = skill._translate_message(message)
        self.assertEqual(tx.type, "test.message2")
        self.assertEqual(tx.data, {"book": "i like reading books"})


class _TestSkill(AutotranslatableSkill):
    def __init__(self):
        super().__init__()
        self.skill_id = 'A'


class SimpleSkill1(_TestSkill):
    def __init__(self):
        super(SimpleSkill1, self).__init__()

    """ Test skill for message data key translations """

    def initialize(self):
        self.translate_keys = ["book"]


class SimpleSkill2(_TestSkill):
    """ Test skill for calling translate message """
    skill_id = 'A'

    def initialize(self):
        self.message_tx_called = False
        self.handler_called = False

    def _translate_message(self, message, lang=None):
        self.message_tx_called = True

    def call_intent(self, message=None):
        handler = self.handler

        # this is what the AutoTranslatableSkill class does
        def universal_intent_handler(message, dummy=None):
            message = self._translate_message(message)
            handler(message)

        universal_intent_handler(message)

    def handler(self, message):
        self.handler_called = True
