"""
Test for shared functionality
"""
import unittest
import os
from pyauthenticator.share import \
    expand_path, \
    load_config, \
    write_config, \
    get_otpauth_dict, \
    add_padding, \
    check_if_key_in_config


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

    def test_add_padding(self):
        main_str = "1234"
        padding_str = "0"
        str_pad_0 = add_padding(
            main_str=main_str,
            padding_str=padding_str,
            padding_length=5
        )
        str_pad_1 = add_padding(
            main_str=main_str,
            padding_str=padding_str,
            padding_length=6,
            inverse_padding=True
        )
        str_pad_2 = add_padding(
            main_str=main_str,
            padding_str=padding_str,
            padding_length=7,
            inverse_padding=False
        )
        self.assertEqual("12340", str_pad_0)
        self.assertEqual("001234", str_pad_1)
        self.assertEqual("1234000", str_pad_2)

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
