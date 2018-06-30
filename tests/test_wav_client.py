import unittest
from mycroft_jarbas_utils.clients.wav import FileConsumer
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


class TestWavClient(unittest.TestCase):
    emitter = MockEmitter()

    def setUp(self):
        self.emitter.reset()

    def test_file_stt(self):
        f = FileConsumer(emitter=self.emitter)

        # test no stt engine init
        message = Message("stt.request",
                          {"File": "hello_world.wav"})
        f.handle_external_request(message)
        result_list = [{'error': 'STT initialization failure'}]
        for type in self.emitter.get_types():
            self.assertEqual(type, 'stt.error')
        self.assertEqual(sorted(self.emitter.get_results()),
                         sorted(result_list))
        self.emitter.reset()

        # test no file
        message = Message("stt.request")
        f.init_stt()
        f.handle_external_request(message)
        result_list = [
            {'error': 'No file provided for transcription'}]
        for type in self.emitter.get_types():
            self.assertEqual(type, 'stt.error')
        self.assertEqual(sorted(self.emitter.get_results()),
                         sorted(result_list))
        self.emitter.reset()

        # test bad file path
        message = Message("stt.request",
                          {"File": "no.wav"})
        f.init_stt()
        f.handle_external_request(message)
        result_list = [
            {'error': 'Invalid file path provided for transcription'}]
        for type in self.emitter.get_types():
            self.assertEqual(type, 'stt.error')
        self.assertEqual(sorted(self.emitter.get_results()),
                         sorted(result_list))
        self.emitter.reset()

        # test bad file format
        message = Message("stt.request",
                          {"File": "jarbas.mp3"})
        f.init_stt()
        f.handle_external_request(message)
        result_list = [
            {'error': 'Invalid file format provided for transcription'}]
        for type in self.emitter.get_types():
            self.assertEqual(type, 'stt.error')
        self.assertEqual(sorted(self.emitter.get_results()),
                         sorted(result_list))
        self.emitter.reset()

        # test stt engine init
        message = Message("stt.request",
                          {"File": "hello_world.wav"})
        f.init_stt()
        f.handle_external_request(message)
        result_list = [{'transcription': 'hello world'}]
        for type in self.emitter.get_types():
            self.assertEqual(type, 'stt.reply')
        self.assertEqual(sorted(self.emitter.get_results()),
                         sorted(result_list))
        self.emitter.reset()


if __name__ == "__main__":
    unittest.main()
