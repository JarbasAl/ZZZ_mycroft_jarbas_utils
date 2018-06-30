# -*- coding: iso-8859-15 -*-
#
# Copyright 2017 Mycroft AI Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import unittest
from mycroft_jarbas_utils.ssml import SSMLBuilder


class TestSSML(unittest.TestCase):
    def test_ssml_builder(self):
        ssml = "<speak>Prosody can be used to change the way words " \
               "sound. The following words are " \
               "<prosody volume='1.6'>" \
               "quite a bit louder than the rest of this passage." \
               "</prosody> Each morning when I wake up, " \
               "<prosody rate='0.4'>I speak quite slowly and " \
               "deliberately until I have my coffee.</prosody> I can " \
               "also change the pitch of my voice using prosody. " \
               "Do you like <prosody pitch='+10%'>speech with a pitch " \
               "that is higher, </prosody> or <prosody pitch='-10%'>" \
               "is a lower pitch preferable?</prosody></speak>"

        s = SSMLBuilder(ssml_tag=False)
        s.say("Prosody can be used to change the way words sound. "
              "The following words are ")
        s.say_loud("quite a bit louder than the rest of this passage.")
        s.say("Each morning when I wake up, ")
        s.say_slow("I speak quite slowly and "
                   "deliberately until I have my coffee.")
        s.say("I can also change the pitch of my voice using prosody. "
              "Do you like")
        s.say_high_pitch("speech with a pitch that is higher, ")
        s.say("or")
        s.say_low_pitch("is a lower pitch preferable?")
        result = s.build()

        self.assertEqual(ssml, result)


if __name__ == "__main__":
    unittest.main()
