import os
import unittest
from typing import Dict

from pyauthenticator import get_two_factor_code, write_qrcode_to_file
from pyauthenticator.share import config_file, expand_path, write_config


class TestUserInterface(unittest.TestCase):
    config_dict: Dict[str, str]
    config_path: str

    @classmethod
    def setUpClass(cls) -> None:
        cls.config_dict = {
            "test": "otpauth://totp/Test%3A%20root%40github.com?secret=6IQXETC4ADOSMMUN&issuer=Test"
        }
        cls.config_path = expand_path(config_file)
        if not os.path.exists(cls.config_path):
            write_config(
                config_dict=cls.config_dict
            )

    def test_get_two_factor_code(self) -> None:
        code = get_two_factor_code(service="test")
        self.assertEqual(len(code), 6)

    def test_write_qrcode_to_file(self) -> None:
        write_qrcode_to_file(service="test")
        self.assertTrue(os.path.exists("test.png"))


if __name__ == '__main__':
    unittest.main()
