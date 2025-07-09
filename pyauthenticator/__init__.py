"""
Generate two factor authentication codes on the command line
"""

from . import _version
from pyauthenticator.share import generate_qrcode
from pyauthenticator.share import get_two_factor_code as get_two_factor_code_internal
from pyauthenticator.share import load_config

__version__ = _version.__version__


def write_qrcode_to_file(service, file_name=None):
    """
    Write qrcode to file to scan it with a mobile application

    Args:
        service (str): lower case name of the service
        file_name (str/ None): default file name <service.png>
    """
    generate_qrcode(key=service, config_dict=load_config(), file_name=file_name)


def get_two_factor_code(service):
    """
    Generate two factor authentication code

    Args:
        service (str): lower case name of the service

    Returns:
        str: two factor authentication code
    """
    return get_two_factor_code_internal(
        key=service,
        config_dict=load_config(),
    )
