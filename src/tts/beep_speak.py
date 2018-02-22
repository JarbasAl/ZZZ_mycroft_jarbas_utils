import time
from os.path import exists
from mycroft.util import play_wav
from mycroft.util.log import LOG
from mycroft.tts import TTS, TTSValidator
from mycroft.configuration import ConfigurationManager
from mycroft import MYCROFT_ROOT_PATH


__author__ = 'jarbas'

# you need to change mycroft/tts/__init__.py
# https://github.com/JarbasAl/beep_speak_tts/blob/master/tts/__init__.py#L388

# you need the sound files
# https://github.com/JarbasAl/beep_speak_tts/tree/master/res/snd/beep_speak


class BeepSpeak(TTS):
    def __init__(self, lang="en-us", voice="r2d2"):
        super(BeepSpeak, self).__init__(lang, voice, BeepSpeakValidator(self))
        config = ConfigurationManager.get().get("tts").get("beep_speak", {})
        self.time_step = float(config.get("time_step", 0.3))
        self.voice = config.get("voice", voice)
        self.lang = config.get("lang", lang)
        self.sound_files_path = config.get("path", MYCROFT_ROOT_PATH +
                                           "/mycroft/res/snd/beep_speak")

        # support these chars
        self.code = ["?", "!", ".", "+", "-", "*", "A", "B", "C", "D", "E",
                     "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P",
                     "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "1",
                     "2", "3", "4", "5", "6", "7", "8", "9", "0"]

    def verify(self, string):
        for char in string:
            if char.upper() not in self.code and char != ' ':
                LOG.debug('Error the character ' + char + ' cannot be ' \
                                                      'translated to ' \
                                                      'beep_speak')
                string.replace(char.upper(), "").replace(char, "")
        return string

    def execute(self, msg):

        msg = self.verify(msg)

        for char in msg:
            if char == ' ':
                time.sleep(2 * self.time_step)
            else:
                beep_sound_path = self.sound_files_path + "/" + \
                                   char.upper() + '_beep.wav'
                play_wav(beep_sound_path)
                time.sleep(self.time_step)  # ~sound duration


class BeepSpeakValidator(TTSValidator):
    def __init__(self, tts):
        super(BeepSpeakValidator, self).__init__(tts)

    def validate_lang(self):
        pass

    def validate_connection(self):
        path = self.tts.sound_files_path
        if not exists(path):
            raise EnvironmentError("beep speak sound files missing: " +
                                   path)

    def get_tts_class(self):
        return BeepSpeak