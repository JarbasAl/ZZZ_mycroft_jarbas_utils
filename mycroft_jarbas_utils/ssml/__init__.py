import re


class SSMLBuilder(object):
    def __init__(self):
        self.text = "<ssml><speak>"
        self.ssml_tags = ["speak", "ssml", "phoneme", "voice", "audio", "prosody"]

    def audio(self, audio_file, text=""):
        if len(self.text) and not self.text.endswith(" "):
            self.text += " "
        self.text += '<audio src=' + audio_file + '>' + text + '</audio>'

    def pause(self):
        if len(self.text) and not self.text.endswith(" "):
            self.text += " "
        self.text += "<break />"

    def prosody(self, text, arg):
        if len(self.text) and not self.text.endswith(" "):
            self.text += " "
        self.text += "<prosody " + arg + ">" + text + "</prosody> "

    def pitch(self, pitch, text=""):
        if len(self.text) and not self.text.endswith(" "):
            self.text += " "
        self.text += "<prosody pitch='" + str(pitch) + "'>" + text + "</prosody> "

    def volume(self, volume, text=""):
        if len(self.text) and not self.text.endswith(" "):
            self.text += " "
        self.text += "<prosody volume='" + volume + "'>" + text + "</prosody> "

    def rate(self, rate, text=""):
        if len(self.text) and not self.text.endswith(" "):
            self.text += " "
        self.text += "<prosody rate='" + rate + "'>" + text + "</prosody> "

    def speak(self, text):
        if len(self.text) and not self.text.endswith(" "):
            self.text += " "
        self.text += text

    def speak_loud(self, text):
        self.volume("1.6", text)

    def speak_slow(self, text):
        self.rate("0.4", text)

    def speak_fast(self, text):
        self.rate("1.6", text)

    def speak_low_pitch(self, text):
        self.pitch("-10%", text)

    def speak_high_pitch(self, text):
        self.pitch("+10%", text)

    def phoneme(self, ph, text=""):
        if len(self.text) and not self.text.endswith(" "):
            self.text += " "
        self.text += "<phoneme ph=" + ph + ">" + text + "</phoneme> "

    def voice(self, voice, text):
        if len(self.text) and not self.text.endswith(" "):
            self.text += " "
        self.text += "<voice name=" + voice + ">" + text + "</voice> "

    def whisper(self, text):
        if len(self.text) and not self.text.endswith(" "):
            self.text += " "
        self.text += "<whispered>" + text + "<\whispered> "

    def build(self):
        self.text = self.text.strip() + "</speak></ssml>"
        return self.text

    @staticmethod
    def remove_ssml(text):
        return re.sub('<[^>]*>', '', text).replace('  ', ' ')

    @staticmethod
    def extract_ssml_tags(text):
        # find ssml tags in string
        return re.findall('<[^>]*>', text)
