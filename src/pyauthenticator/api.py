"""
Shared functionality to generate two factor authentication codes
"""

from typing import Any, Dict, List, Optional

from pyauthenticator._core import decode_qrcode, encode_qrcode, get_totp
from pyauthenticator._config import default_config_file, write_config


def get_totp_for_key_in_dict(key: str, config_dict: Dict[str, Any]) -> str:
    """
    Generate the two factor authentication code

    Args:
        key (str): lower case name of the service
        config_dict (dict): configuration dictionary

    Returns:
        str: two factor authentication code as string
    """
    return get_totp(otpauth_str=config_dict[key])


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
    config_dict[key] = decode_qrcode(qrcode_png_file_name=qrcode_png_file_name)
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
    encode_qrcode(otpauth_str=config_dict[key], file_name=file_name)


def list_services(config_dict: Dict[str, Any]) -> List[str]:
    """
    List available services

    Args:
        config_dict (dict): configuration dictionary

    Returns:
        list: list of available services
    """
    return list(config_dict.keys())
