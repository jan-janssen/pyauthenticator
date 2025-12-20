import os
import unittest
import json

from pyauthenticator import get_two_factor_code, write_qrcode_to_file, add_two_factor_provider, list_two_factor_providers
from pyauthenticator._config import default_config_file, write_config, load_config


class TestUserInterface(unittest.TestCase):
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

    def test_get_two_factor_code(self):
        code = get_two_factor_code(service="test")
        self.assertEqual(len(code), 6)

    def test_write_qrcode_to_file(self):
        write_qrcode_to_file(service="test")
        self.assertTrue(os.path.exists("test.png"))

    def test_add_and_list_providers(self):
        """
        Test adding and listing two-factor providers.
        """
        # Ensure the provider does not exist
        providers = list_two_factor_providers()
        self.assertNotIn("new_test_service", providers)

        # Create a dummy qr code file
        qr_code_file = "test_qr_add.png"
        import qrcode
        qrcode.make("otpauth://totp/Test?secret=JBSWY3DPEHPK3PXP&issuer=Test").save(qr_code_file, "PNG")

        # Add the provider
        add_two_factor_provider("new_test_service", qr_code_file)

        # Check if the provider was added
        providers = list_two_factor_providers()
        self.assertIn("new_test_service", providers)

        # Clean up the config file and the qr code file
        config = load_config()
        del config["new_test_service"]
        write_config(config)
        os.remove(qr_code_file)


if __name__ == '__main__':
    unittest.main()
