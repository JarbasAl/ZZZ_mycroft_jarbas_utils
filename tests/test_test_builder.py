import unittest
from mycroft_jarbas_utils.intent.tests import IntentTestBuilder


class TestIntentTestBuilder(unittest.TestCase):
    def test_IntentTestBuilder(self):
        def basic_test():
            t = IntentTestBuilder()

            ### before testing

            t.remove_context("OldContext")
            t.set_context("Testing", "this is a test")
            # what are we testing
            t.test_utterance("i said this")

            ### tests

            # IntentBuilder("MyIntent")
            t.check_intent("MyIntent")
            # .require("person").require("verb")
            t.check_keyword("person", "i")
            t.check_keyword("verb", "said")
            # self.speak_dialog("test")
            t.check_dialog_file("test")

            # build the test
            return t.build_test()

        self.assertEqual(basic_test(), {
            'intent_type': 'MyIntent',
            'intent':
                {
                    'person': 'i',
                    'verb': 'said'
                },
            'remove_context': ['OldContext'],
            'changed_context': [],
            'set_context': {'Testing': 'this is a test'},
            'expected_dialog': 'test',
            'evaluation_timeout': 30,
            'utterance': 'i said this'
        }
                         )


if __name__ == "__main__":
    unittest.main()
