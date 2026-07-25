import base64
import os
import tempfile
import unittest

from pyauthenticator._config import load_config, write_config
from pyauthenticator.api import generate_qrcode


try:
    from pyauthenticator.mcp_server import (
        add_service,
        get_code,
        get_qrcode,
        list_services,
        mcp,
        remove_service,
    )
    disable_mcp_tests = False
except ImportError:
    disable_mcp_tests = True


@unittest.skipIf(disable_mcp_tests, "mcp optional dependency not installed")
class MCPServerTest(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.old_home = os.environ.get("HOME")
        os.environ["HOME"] = self.tmp_dir.name
        self.config_dict = {
            "test": "otpauth://totp/Test%3A%20root%40github.com?secret=6IQXETC4ADOSMMUN&issuer=Test"
        }
        write_config(config_dict=self.config_dict)
        self.qr_code_png = os.path.join(self.tmp_dir.name, "test.png")
        generate_qrcode(
            key="test",
            config_dict=self.config_dict,
            file_name=self.qr_code_png,
        )

    def tearDown(self):
        if self.old_home is None:
            del os.environ["HOME"]
        else:
            os.environ["HOME"] = self.old_home
        self.tmp_dir.cleanup()

    def test_list_services_and_get_code(self):
        self.assertEqual(["test"], list_services())
        self.assertEqual(len(get_code(service="test")), 6)

    def test_add_service_from_path_and_remove_service(self):
        self.assertEqual(
            add_service(service="test2", qrcode_path=self.qr_code_png),
            "The service 'test2' was added, from file <" + self.qr_code_png + ">.",
        )
        self.assertTrue("test2" in load_config().keys())
        self.assertEqual(
            remove_service(service="test2"), "The service 'test2' was removed."
        )
        self.assertTrue("test2" not in load_config().keys())

    def test_add_service_from_base64(self):
        with open(self.qr_code_png, "rb") as f:
            qrcode_base64 = base64.b64encode(f.read()).decode("utf-8")
        self.assertEqual(
            add_service(service="test2", qrcode_base64=qrcode_base64),
            "The service 'test2' was added from the provided QR code.",
        )
        self.assertEqual(load_config()["test2"], self.config_dict["test"])

    def test_add_service_requires_single_source(self):
        with self.assertRaisesRegex(
            ValueError, "Provide exactly one of qrcode_path or qrcode_base64"
        ):
            add_service(service="test2")
        with self.assertRaisesRegex(
            ValueError, "Provide exactly one of qrcode_path or qrcode_base64"
        ):
            add_service(
                service="test2",
                qrcode_path=self.qr_code_png,
                qrcode_base64="Zm9v",
            )

    def test_add_service_rejects_invalid_base64(self):
        with self.assertRaisesRegex(
            ValueError, "qrcode_base64 must be valid base64-encoded PNG data"
        ):
            add_service(service="test2", qrcode_base64="!!!")

    def test_get_qrcode(self):
        qrcode_image = get_qrcode(service="test")
        image_content = qrcode_image.to_image_content()
        self.assertEqual(image_content.mimeType, "image/png")
        self.assertTrue(len(image_content.data) > 0)

    def test_unknown_service_errors_include_available_services(self):
        with self.assertRaisesRegex(
            ValueError,
            'The service "missing" does not exist.\n\n'
            "The config file ~/.pyauthenticator contains the following services:\n"
            "  \\* test\n\n"
            "Choose one of these or add a new service using:\n"
            "  pyauthenticator --add <qr-code.png> <servicename>",
        ):
            get_code(service="missing")
        with self.assertRaisesRegex(
            ValueError,
            'The service "missing" does not exist.\n\n'
            "The config file ~/.pyauthenticator contains the following services:\n"
            "  \\* test\n\n"
            "Choose one of these or add a new service using:\n"
            "  pyauthenticator --add <qr-code.png> <servicename>",
        ):
            remove_service(service="missing")

    def test_unknown_service_errors_when_config_is_empty(self):
        write_config(config_dict={})
        with self.assertRaisesRegex(
            ValueError,
            "The config file ~/.pyauthenticator does not contain any services. "
            "To add a new service use:\n"
            "  pyauthenticator --add <qr-code.png> <servicename>",
        ):
            get_qrcode(service="missing")

    def test_tools_are_registered(self):
        self.assertEqual(
            set(mcp._tool_manager._tools.keys()),
            {
                "add_service",
                "get_code",
                "get_qrcode",
                "list_services",
                "remove_service",
            },
        )


if __name__ == "__main__":
    unittest.main()
