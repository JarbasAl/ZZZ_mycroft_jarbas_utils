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
from mycroft_jarbas_utils.mark1.faceplate import mouth_display_txt

draw = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX\n" \
       "XXXXXXXXXXXXXX     XXXXXXXXXXXXX\n" \
       "XXXXXXXXXXXXXX     XXXXXXXXXXXXX\n" \
       "XXXXXXXXXXXXXX XXX XXXXXXXXXXXXX\n" \
       "XXXXXXXXXXXXXX XXX XXXXXXXXXXXXX\n" \
       "XXXXXXXXXXXXX  XX  XXXXXXXXXXXXX\n" \
       "XXXXXXXXXXXX   X   XXXXXXXXXXXXX\n" \
       "XXXXXXXXXXXXX XXX XXXXXXXXXXXXXX"


class TestMark1Utils(unittest.TestCase):
    def test_draw_from_txt(self):
        self.assertEqual(mouth_display_txt(draw, is_file=False),
                         "aIAAAAAAAAAAAAAAAAAAAAAAAAAEAOOHGAGEGOOHAAAAAAAAAAAAAAAAAAAAAAAAAA")


if __name__ == "__main__":
    unittest.main()
