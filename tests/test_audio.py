import unittest
from mycroft_jarbas_utils.skills.audio import AudioSkill
from mycroft.messagebus.message import Message
from os.path import exists
from os import makedirs, remove
from adapt.intent import IntentBuilder


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


class AudioSkillTest(unittest.TestCase):
    emitter = MockEmitter()

    def setUp(self):
        self.emitter.reset()

    # test initialization of audio service
    def test_audio_init(self):
        skill = _TestSkill()
        skill.bind(self.emitter)
        skill.load_data_files("test_skill")
        skill.initialize()
        assert skill.audio is not None

    # test adding backends as optional keywords
    def check_register_intent(self, result_list):
        for type in self.emitter.get_types():
            self.assertEquals(type, 'register_intent')
        self.assertEquals(sorted(self.emitter.get_results()),
                          sorted(result_list))
        self.emitter.reset()

    def test_register_intent(self):
        # Test register Intent object
        skill = SimpleSkill2()
        skill.bind(self.emitter)
        skill.load_data_files("test_skill")
        self.emitter.reset()
        skill.initialize()
        expected = [{'at_least_one': [],
                     'name': 'A:a',
                     'optional': [('AudioBackend', 'AudioBackend')],
                     'requires': [('AKeyword', 'AKeyword')]}]
        self.check_register_intent(expected)

        # Test register IntentBuilder object
        skill = SimpleSkill2()
        skill.bind(self.emitter)
        skill.load_data_files("test_skill")
        self.emitter.reset()
        skill.initialize()
        expected = [{'at_least_one': [],
                     'name': 'A:a',
                     'optional': [('AudioBackend', 'AudioBackend')],
                     'requires': [('AKeyword', 'AKeyword')]}]

        self.check_register_intent(expected)

    # test creating of vocabulary for audio backend names
    def test_backend_vocabulary(self):
        skill = _TestSkill()
        skill.bind(self.emitter)
        skill.load_data_files("test_skill")
        skill.initialize()
        backend_kw = [
            {'file_name': 'test_skill/vocab/en-us/AudioBackend.entity',
             'name': 'A:AudioBackend'}]

        for backend in skill.backends:
            backend_kw.append({"start": backend,
                               'end': 'AAudioBackend'})

            for m in skill._modifiers:
                backend_kw.append({"start": m + " " + backend,
                                   'end': 'AAudioBackend'})

        for backend in self.emitter.get_results():
            assert backend in backend_kw

        self.emitter.reset()

    def test_backend_entity_file_creation(self):
        if not exists("test_skill/vocab/en-us"):
            makedirs("test_skill/vocab/en-us")
        if exists("test_skill/vocab/en-us/AudioBackend.entity"):
            remove("test_skill/vocab/en-us/AudioBackend.entity")
        skill = _TestSkill()
        skill.bind(self.emitter)
        skill.load_data_files("test_skill")
        skill.initialize()
        assert exists("test_skill/vocab/en-us/AudioBackend.entity")

    # test injecting audiobackend data in message
    def test_inject(self):
        skill = _TestSkill()
        skill.bind(self.emitter)
        skill.load_data_files("test_skill")
        skill.initialize()
        message = Message("test", {"some_data": {}})
        result = Message("test", {"AudioBackend": "",
                                  "some_data": {}})
        self.assertEqual(skill._clean_message(message).data, result.data)

    # test filtering backend names from message.data fields
    def test_filters(self):
        skill = _TestSkill()
        skill.bind(self.emitter)
        skill.load_data_files("test_skill")
        skill.initialize()
        skill.add_filter("music")
        message = Message("test", {"music": "play satanic black metal in vlc"})
        result = Message("test", {"AudioBackend": "",
                                  "music": "play satanic black metal "})
        self.assertEqual(skill._clean_message(message).data, result.data)


class _TestSkill(AudioSkill):
    def __init__(self):
        super().__init__()
        self.skill_id = 'A'


class SimpleSkill1(_TestSkill):
    def __init__(self):
        super(SimpleSkill1, self).__init__()
        self.handler_run = False

    """ Test skill for normal intent builder syntax """

    def initialize(self):
        i = IntentBuilder('a').require('Keyword').build()
        self.register_intent(i, self.handler)

    def handler(self, message):
        self.handler_run = True

    def stop(self):
        pass


class SimpleSkill2(_TestSkill):
    """ Test skill for intent builder without .build() """
    skill_id = 'A'

    def initialize(self):
        i = IntentBuilder('a').require('Keyword')
        self.register_intent(i, self.handler)
        self.handler_called = False

    def handler(self, message):
        self.handler_called = True
