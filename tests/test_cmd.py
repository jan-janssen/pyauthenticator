import json
import os
import subprocess
import unittest
from contextlib import redirect_stdout
from io import StringIO

from pyauthenticator.__main__ import command_line_parser
from pyauthenticator.config import default_config_file, write_config


class CmdSubprocessTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config_dict = {
            "test": "otpauth://totp/Test%3A%20root%40github.com?secret=6IQXETC4ADOSMMUN&issuer=Test"
        }
        cls.config_path = os.path.abspath(os.path.expanduser(default_config_file))
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
        self.assertTrue("test2" in config_dict.keys())


class CmdParserTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config_dict = {
            "test": "otpauth://totp/Test%3A%20root%40github.com?secret=6IQXETC4ADOSMMUN&issuer=Test"
        }
        cls.config_path = os.path.abspath(os.path.expanduser(default_config_file))
        if not os.path.exists(cls.config_path):
            write_config(
                config_dict=cls.config_dict
            )

    def test_main_generate_two_factor(self):
        with redirect_stdout(StringIO()) as sout:
            command_line_parser(cmd_args=["test"])
        self.assertEqual(len(sout.getvalue().rstrip('\n')), 6)
        with redirect_stdout(StringIO()) as sout:
            command_line_parser(cmd_args=["test3"])
        self.assertEqual(
            sout.getvalue().split("\n")[0],
            "The service \"test3\" does not exist."
        )

    def test_main_generate_qr_code(self):
        with redirect_stdout(StringIO()) as sout:
            command_line_parser(cmd_args=["-qr", "test"])
        self.assertEqual(
            sout.getvalue(),
            "The qrcode file <test.png> was generated.\n"
        )
        self.assertTrue(os.path.exists("test.png"))
        with redirect_stdout(StringIO()) as sout:
            command_line_parser(cmd_args=["-a", "test.png", "test4"])
        self.assertEqual(
            sout.getvalue(),
            "The service 'test4' was added, from file <test.png>.\n"
        )
        with open(self.config_path, "r") as f:
            config_dict = json.load(f)
        self.assertTrue("test4" in config_dict.keys())


if __name__ == '__main__':
    unittest.main()
