"""
Test for shared functionality
"""
import os
import unittest

from pyauthenticator.share import (
    check_if_key_in_config,
    expand_path,
    get_otpauth_dict,
    load_config,
    write_config
)


class ShareTest(unittest.TestCase):
    def test_expand_path(self):
        test_path = "~/.pyauthenticator"
        self.assertEqual(
            expand_path(path=test_path),
            os.path.abspath(
                os.path.expanduser(
                    test_path
                )
            )
        )

    def test_config(self):
        test_file_name = "test.json"
        test_dict = {"key": "value"}
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

    def test_get_otpauth_dict(self):
        otpauth_str = "otpauth://totp/Test%3A%20root%40github.com?secret=MAGICSECRET&issuer=Test"
        otpauth_dict = get_otpauth_dict(
            otpauth_str=otpauth_str
        )
        otp_test_dict = {
            'secret': 'MAGICSECRET',
            'issuer': 'Test'
        }
        self.assertDictEqual(otpauth_dict, otp_test_dict)

    def test_check_if_key_in_config(self):
        test_dict = {"key": "value"}
        check_if_key_in_config(
            key="key",
            config_dict=test_dict
        )
        with self.assertRaises(ValueError):
            check_if_key_in_config(
                key="secret",
                config_dict=test_dict
            )


if __name__ == '__main__':
    unittest.main()
