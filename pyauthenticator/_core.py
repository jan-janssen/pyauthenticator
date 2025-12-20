"""
Core functionality to generate two factor authentication codes
"""

from typing import Any

import pyotp
import qrcode
from PIL import Image
from pyzbar.pyzbar import decode


def decode_qrcode(qrcode_png_file_name: str) -> str:
    """
    Decode qrcode from png file

    Args:
        qrcode_png_file_name (str): path to the png file which contains the qr code

    Returns:
        str: decoded otpauth string
    """
    return decode(Image.open(qrcode_png_file_name))[0].data.decode("utf-8")


def encode_qrcode(otpauth_str: str, file_name: str) -> None:
    """
    Encode otpauth string into qrcode image saved as png file

    Args:
        otpauth_str (str): otpauth string
        file_name (str): path to the png file which will contain the qr code
    """
    qrcode.make(otpauth_str).save(file_name, "PNG")


def get_totp(otpauth_str: str) -> str:
    """
    Get TOTP code for a specific service based on its otpauth dictionary

    Args:
        otpauth_str (str): otpauth string for the service

    Returns:
        str: TOTP code for the service
    """
    otpauth_dict = {
        kv[0]: kv[1]
        for kv in [
            otpvar.split("=") for otpvar in otpauth_str.replace("?", "&").split("&")[1:]
        ]
    }

    kwargs: dict[str, Any] = {}
    if "digits" in otpauth_dict.keys():
        kwargs["digits"] = int(otpauth_dict["digits"])
    if "period" in otpauth_dict.keys():
        kwargs["interval"] = int(otpauth_dict["period"])
    if "issuer" in otpauth_dict.keys():
        kwargs["issuer"] = otpauth_dict["issuer"]
    return pyotp.TOTP(
        **kwargs,
        s=otpauth_dict["secret"],
    ).now()
