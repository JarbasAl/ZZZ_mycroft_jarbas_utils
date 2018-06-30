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
from mycroft_jarbas_utils.phonemes import get_phonemes, guess_phonemes


class TestPhonemes(unittest.TestCase):
    def test_get_phonemes(self):
        self.assertEqual(get_phonemes("hey mycroft"),
                         "HH EY1 . M Y K R OW F T")
        self.assertEqual(get_phonemes("hey computer"),
                         "HH EY1 . K AH0 M P Y UW1 T ER0")
        self.assertEqual(get_phonemes("hey jarbas"), "HH EY1 . JH AE R B AE S")
        self.assertEqual(get_phonemes("thank you"), "TH AE1 NG K . Y UW1")
        self.assertEqual(get_phonemes("alexa"), "AH0 L EH1 K S AH0")

    def test_guess_phonemes(self):
        self.assertEqual(guess_phonemes("mycroft"),
                         ['M', 'Y', 'K', 'R', 'OW', 'F', 'T'])
        self.assertEqual(guess_phonemes("computer"),
                         ['K', 'OW', 'M', 'P', 'AH', 'T', 'EH', 'R'])
        self.assertEqual(guess_phonemes("jarbas"),
                         ['JH', 'AE', 'R', 'B', 'AE', 'S'])
        self.assertEqual(guess_phonemes("thank you"), None)
        self.assertEqual(
            guess_phonemes("thank") + ["."] + guess_phonemes("you"),
            ['TH', 'AE', 'N', 'K', '.', 'Y', 'OW', 'AH'])
        self.assertEqual(guess_phonemes("alexa"),
                         ['AE', 'L', 'EH', 'K', 'S', 'AE'])


if __name__ == "__main__":
    unittest.main()
