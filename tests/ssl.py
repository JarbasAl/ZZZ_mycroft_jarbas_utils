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
