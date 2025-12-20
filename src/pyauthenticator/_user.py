"""
Generate two factor authentication codes on the command line
"""

from typing import Optional
from pyauthenticator._config import default_config_file, load_config
from pyauthenticator.api import (
    add_service,
    generate_qrcode,
    get_totp_for_key_in_dict,
    list_services,
)


def write_qrcode_to_file(service: str, file_name: Optional[str] = None) -> None:
    """
    Write qrcode to file to scan it with a mobile application

    Args:
        service (str): lower case name of the service
        file_name (str/ None): default file name <service.png>
    """
    generate_qrcode(key=service, config_dict=load_config(), file_name=file_name)


def get_two_factor_code(service: str) -> str:
    """
    Generate two factor authentication code

    Args:
        service (str): lower case name of the service

    Returns:
        str: two factor authentication code
    """
    return get_totp_for_key_in_dict(
        key=service,
        config_dict=load_config(),
    )


def add_two_factor_provider(service: str, qrcode_png_file_name: str) -> None:
    """
    Add new two factor authentication provider to configuration file

    Args:
        service (str): lower case name of the service
        qrcode_png_file_name (str): path to the png file which contains the qr code
    """
    add_service(
        key=service,
        qrcode_png_file_name=qrcode_png_file_name,
        config_dict=load_config(),
        config_file_to_write=default_config_file,
    )


def list_two_factor_providers() -> list[str]:
    """
    List all two factor authentication providers in the configuration file

    Returns:
        list[str]: list of two factor authentication providers
    """
    return list_services(config_dict=load_config())
