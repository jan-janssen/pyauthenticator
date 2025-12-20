"""
Tests for the pyauthenticator.config module
"""
import unittest
import os
from pyauthenticator._config import load_config, write_config

class TestConfig(unittest.TestCase):
    """
    Tests for the config module
    """
    def setUp(self):
        self.config_file = 'test_config.json'
        self.config_data = {'service': 'otpauth://totp/Test?secret=SECRET&issuer=Test'}

    def tearDown(self):
        if os.path.exists(self.config_file):
            os.remove(self.config_file)

    def test_load_config_non_existent(self):
        """
        Test loading a non-existent config file
        """
        self.assertEqual(load_config('non_existent_file.json'), {})

    def test_write_and_load_config(self):
        """
        Test writing and loading a config file
        """
        write_config(self.config_data, self.config_file)
        self.assertTrue(os.path.exists(self.config_file))
        loaded_data = load_config(self.config_file)
        self.assertEqual(loaded_data, self.config_data)


if __name__ == '__main__':
    unittest.main()
