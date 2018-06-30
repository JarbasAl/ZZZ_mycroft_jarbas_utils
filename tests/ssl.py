import unittest
from os.path import exists, join, expanduser
from os import remove
from mycroft_jarbas_utils.ssl import create_self_signed_cert


class TestSSL(unittest.TestCase):
    def test_self_signed(self):
        name = "self_signed_jarbas"
        path = expanduser("~")
        create_self_signed_cert(path, name)
        assert exists(join(path, name + ".crt"))
        remove(join(path, name + ".crt"))
        assert exists(join(path, name + ".key"))
        remove(join(path, name + ".key"))


if __name__ == "__main__":
    unittest.main()
