import json
import os
import runpy
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

from pyauthenticator._cmd import command_line_parser
from pyauthenticator._config import default_config_file, write_config


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
        try:
            code = subprocess.check_output(
                ["coverage", "run", "-a", "-m", "pyauthenticator", "test"],
                universal_newlines=True
            )
        except subprocess.CalledProcessError as e:
            print(e.output)
            code = ""
        self.assertEqual(len(code.replace("\n", "")), 6)

    def test_main_generate_qr_code(self):
        try:
            subprocess.check_output(
                ["coverage", "run", "-a", "-m", "pyauthenticator", "-qr", "test"],
                universal_newlines=True
            )
        except subprocess.CalledProcessError as e:
            print(e.output)
        self.assertTrue(os.path.exists("test.png"))
        try:
            subprocess.check_output(
                ["coverage", "run", "-a", "-m", "pyauthenticator", "-a", "test.png", "test2"],
                universal_newlines=True
            )
        except subprocess.CalledProcessError as e:
            print(e.output)
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

    def test_no_service(self):
        """
        Test calling the command line parser without a service.
        """
        with self.assertRaises(SystemExit):
            with redirect_stdout(StringIO()):
                command_line_parser(cmd_args=[])

    def test_help(self):
        """
        Test calling the command line parser with the --help argument.
        """
        with self.assertRaises(SystemExit):
            with redirect_stdout(StringIO()):
                command_line_parser(cmd_args=["--help"])

    def test_version(self):
        """
        Test the version is imported correctly.
        """
        from pyauthenticator import __version__
        self.assertIsNotNone(__version__)

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

    def test_main_entry_point(self):
        """
        Test the __main__ entry point.
        """
        with patch.object(sys, 'argv', ['pyauthenticator', 'test']):
            runpy.run_module('pyauthenticator', run_name='__main__')

    def test_qr_non_existent_service(self):
        """
        Test generating a QR code for a non-existent service.
        """
        with redirect_stdout(StringIO()) as sout:
            command_line_parser(cmd_args=["-qr", "non_existent_service"])
        self.assertIn("does not exist", sout.getvalue())

class EmptyConfigTest(unittest.TestCase):
    @patch('pyauthenticator._cmd.load_config', return_value={})
    def test_no_services_message(self, mock_load_config):
        """
        Test the message when a service is provided but no services are configured.
        """
        with redirect_stdout(StringIO()) as sout:
            command_line_parser(cmd_args=["some_service"])
        self.assertIn("The config file ~/.pyauthenticator does not contain any services.", sout.getvalue())

    @patch('pyauthenticator._cmd.load_config', return_value={})
    def test_help_with_empty_config(self, mock_load_config):
        """
        Test help message when no services are configured.
        """
        with self.assertRaises(SystemExit):
             with redirect_stdout(StringIO()):
                command_line_parser(cmd_args=["--help"])


if __name__ == '__main__':
    unittest.main()
