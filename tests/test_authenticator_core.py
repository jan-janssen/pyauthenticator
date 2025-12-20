"""
Tests for the pyauthenticator.core module
"""
import unittest
import os
from pyauthenticator._core import decode_qrcode, encode_qrcode, get_totp

class TestAuthenticatorCore(unittest.TestCase):
    """
    Tests for the core module
    """
    def setUp(self):
        self.otpauth_str = "otpauth://totp/Test?secret=JBSWY3DPEHPK3PXP&issuer=Test"
        self.qr_code_file = "test_qr.png"
        self.secret = "JBSWY3DPEHPK3PXP"

    def tearDown(self):
        if os.path.exists(self.qr_code_file):
            os.remove(self.qr_code_file)

    def test_encode_and_decode_qrcode(self):
        """
        Test encoding and decoding a QR code
        """
        encode_qrcode(self.otpauth_str, self.qr_code_file)
        self.assertTrue(os.path.exists(self.qr_code_file))
        decoded_str = decode_qrcode(self.qr_code_file)
        self.assertEqual(decoded_str, self.otpauth_str)

    def test_get_totp(self):
        """
        Test generating a TOTP code
        """
        otpauth_dict = {"secret": self.secret}
        code = get_totp(otpauth_dict)
        self.assertTrue(code.isdigit())
        self.assertEqual(len(code), 6)

    def test_get_totp_with_options(self):
        """
        Test generating a TOTP code with digits and period options
        """
        otpauth_dict = {"secret": self.secret, "digits": "8", "period": "60", "issuer": "Test"}
        code = get_totp(otpauth_dict)
        self.assertTrue(code.isdigit())
        self.assertEqual(len(code), 8)
