import unittest
from mycroft_jarbas_utils.skills.active import ActiveSkill


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


class ActiveSkillTest(unittest.TestCase):
    emitter = MockEmitter()

    def setUp(self):
        self.emitter.reset()

    def test_activate_message(self):
        skill = _TestSkill()
        skill.bind(self.emitter)
        skill.initialize()
        # check that the message to bump to top of converse was sent
        for type in self.emitter.get_types():
            self.assertEqual(type, 'active_skill_request')
        self.emitter.reset()
        # check that the message to bump to top of converse was sent
        # requires PR#1468 to trigger automatically
        # https://github.com/MycroftAI/mycroft-core/pull/1468
        skill.on_deactivate()
        for type in self.emitter.get_types():
            self.assertEqual(type, 'active_skill_request')
        self.emitter.reset()


class _TestSkill(ActiveSkill):
    def __init__(self):
        super().__init__()
        self.skill_id = 'A'
