import unittest
import os
import subprocess
import json
from pyauthenticator.share import expand_path, write_config, config_file


class MyTestCase(unittest.TestCase):
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

    def test_main_generate_two_factor(self):
        code = subprocess.check_output(
            ["coverage", "run", "-a", "pyauthenticator", "test"],
            universal_newlines=True
        )
        self.assertEqual(len(code.replace("\n", "")), 6)

    def test_main_generate_qr_code(self):
        subprocess.check_output(
            ["coverage", "run", "-a", "pyauthenticator", "-qr", "test"],
            universal_newlines=True
        )
        self.assertTrue(os.path.exists("test.png"))
        subprocess.check_output(
            ["coverage", "run", "-a", "pyauthenticator", "-a", "test.png", "test2"],
            universal_newlines=True
        )
        with open(self.config_path, "r") as f:
            config_dict = json.load(f)
        self.assertEqual(len(config_dict.keys()), 2)


if __name__ == '__main__':
    unittest.main()
