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
