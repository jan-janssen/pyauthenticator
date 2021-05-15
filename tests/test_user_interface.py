import unittest
import os
from pyauthenticator import get_two_factor_code, write_qrcode_to_file
from pyauthenticator.share import expand_path, write_config, config_file


class TestUserInterface(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config_dict = {
            "test": "otpauth://totp/Test%3A%20root%40github.com?secret=6IQXETC4ADOSMMUN&issuer=Test"
        }
        cls.config_path = expand_path(config_file)
        if not os.path.exists(cls.config_path):
            write_config(
                config_dict=cls.config_dict
            )

    def test_get_two_factor_code(self):
        code = get_two_factor_code(service="test")
        self.assertEqual(len(code), 6)

    def test_write_qrcode_to_file(self):
        write_qrcode_to_file(service="test")
        self.assertTrue(os.path.exists("test.png"))


if __name__ == '__main__':
    unittest.main()
