"""
Test for core functionality
"""
import os
import unittest

from pyauthenticator._config import load_config
from pyauthenticator.api import (
    add_service,
    generate_qrcode,
    get_totp_for_key_in_dict,
    list_services,
)


class TestCore(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qr_code_png = "test.png"
        cls.config_dict = {
            "test": "otpauth://totp/Test%3A%20root%40github.com?secret=6IQXETC4ADOSMMUN&issuer=Test&period=60&digits=6",
            "test2": "otpauth://totp/Test%3A%20root%40github.com?secret=6IQXETC4ADOSMMUN"
        }
        generate_qrcode(
            key="test",
            config_dict=cls.config_dict,
            file_name=None
        )

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.qr_code_png)

    def test_list_services(self):
        service_lst = list_services(config_dict=self.config_dict)
        self.assertEqual(["test", "test2"], service_lst)

    def test_add_service(self):
        config_file = "test_config.json"
        add_service(
            key="test",
            qrcode_png_file_name=self.qr_code_png,
            config_dict={},
            config_file_to_write=config_file
        )
        config_reload = load_config(config_file_to_load=config_file)
        self.assertEqual(config_reload["test"], self.config_dict["test"])
        os.remove(config_file)

    def test_get_two_factor_code(self):
        code = get_totp_for_key_in_dict(key="test", config_dict=self.config_dict)
        self.assertEqual(len(code), 6)
        code = get_totp_for_key_in_dict(key="test2", config_dict=self.config_dict)
        self.assertEqual(len(code), 6)


if __name__ == '__main__':
    unittest.main()
