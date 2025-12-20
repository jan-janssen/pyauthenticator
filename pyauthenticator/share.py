"""
Shared functionality to generate two factor authentication codes
"""

from inspect import signature
from typing import Any, Dict, List, Optional

import pyotp
import qrcode
from PIL import Image
from pyzbar.pyzbar import decode

from pyauthenticator.config import default_config_file, get_otpauth_dict, write_config


def get_two_factor_code(key: str, config_dict: Dict[str, Any]) -> str:
    """
    Generate the two factor authentication code

    Args:
        key (str): lower case name of the service
        config_dict (dict): configuration dictionary

    Returns:
        str: two factor authentication code as string
    """
    _check_if_key_in_config(key=key, config_dict=config_dict)
    decode_dict_internal = get_otpauth_dict(otpauth_str=config_dict[key])
    funct_sig = signature(pyotp.TOTP)
    if "digits" in decode_dict_internal.keys():
        digits = int(decode_dict_internal["digits"])
    else:
        digits = funct_sig.parameters["digits"].default
    if "period" in decode_dict_internal.keys():
        interval = int(decode_dict_internal["period"])
    else:
        interval = funct_sig.parameters["interval"].default
    if "issuer" in decode_dict_internal.keys():
        issuer = decode_dict_internal["issuer"]
    else:
        issuer = funct_sig.parameters["issuer"].default
    return pyotp.TOTP(
        s=decode_dict_internal["secret"],
        digits=digits,
        issuer=issuer,
        interval=interval,
    ).now()


def add_service(
    key: str,
    qrcode_png_file_name: str,
    config_dict: Dict[str, Any],
    config_file_to_write: str = default_config_file,
) -> None:
    """
    Add new service to configuration file

    Args:
        key (str): lower case name of the service
        qrcode_png_file_name (str): path to the png file which contains the qr code
        config_dict (dict): configuration dictionary
        config_file_to_write (str): path to config file
    """
    otpauth_str = decode(Image.open(qrcode_png_file_name))[0].data.decode("utf-8")
    config_dict[key] = otpauth_str
    write_config(config_dict=config_dict, config_file_to_write=config_file_to_write)


def generate_qrcode(
    key: str, config_dict: Dict[str, Any], file_name: Optional[str] = None
) -> None:
    """
    Write qrcode to file to scan it with a mobile application

    Args:
        key (str): lower case name of the service
        config_dict (dict): configuration dictionary
        file_name (str/ None): default file name <service.png>
    """
    if file_name is None:
        file_name = key + ".png"
    _check_if_key_in_config(key=key, config_dict=config_dict)
    qrcode.make(config_dict[key]).save(file_name, "PNG")


def list_services(config_dict: Dict[str, Any]) -> List[str]:
    """
    List available services

    Args:
        config_dict (dict): configuration dictionary

    Returns:
        list: list of available services
    """
    return list(config_dict.keys())


def _check_if_key_in_config(key: str, config_dict: Dict[str, Any]) -> None:
    """
    Check if a given key is included in a dictionary, raise an ValueError if it is not.

    Args:
        key (str): key as string
        config_dict (dict): configuration dictionary
    """
    if key not in config_dict.keys():
        raise ValueError()
