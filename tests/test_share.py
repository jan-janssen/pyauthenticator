"""
Test for shared functionality
"""
import os
import unittest
from typing import Dict

from pyauthenticator._config import (
    get_otpauth_dict,
    load_config,
    write_config,
)


class ShareTest(unittest.TestCase):
    def test_config(self):
        test_file_name = "test.json"
        test_dict: Dict[str, str] = {"key": "value"}
        write_config(
            config_dict=test_dict,
            config_file_to_write=test_file_name
        )
        test_dict_reload = load_config(
            config_file_to_load=test_file_name
        )
        self.assertDictEqual(test_dict, test_dict_reload)
        test_no_dict = load_config(
            config_file_to_load="no.json"
        )
        self.assertDictEqual(test_no_dict, {})
        os.remove(test_file_name)
        test_dict_reload = load_config(
            config_file_to_load=test_file_name
        )
        self.assertDictEqual({}, test_dict_reload)

    def test_get_otpauth_dict(self):
        otpauth_str = "otpauth://totp/Test%3A%20root%40github.com?secret=MAGICSECRET&issuer=Test"
        otpauth_dict = get_otpauth_dict(
            otpauth_str=otpauth_str
        )
        otp_test_dict: Dict[str, str] = {
            'secret': 'MAGICSECRET',
            'issuer': 'Test'
        }
        self.assertDictEqual(otpauth_dict, otp_test_dict)


if __name__ == '__main__':
    unittest.main()
