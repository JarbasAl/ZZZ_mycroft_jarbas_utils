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
from os.path import exists, join, expanduser
from os import makedirs
from mycroft_jarbas_utils.ssl import create_self_signed_cert


class TestSSL(unittest.TestCase):
    def test_self_signed(self):
        name = "self_signed_jarbas"
        path = join(expanduser("~"), ".jarbas")
        if not exists(path):
            makedirs(path)
        create_self_signed_cert(path, name)
        assert exists(join(path, name + ".crt"))
        assert exists(join(path, name + ".key"))


if __name__ == "__main__":
    unittest.main()
