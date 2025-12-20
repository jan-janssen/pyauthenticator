"""
Generate two factor authentication codes on the command line
"""

from . import _version
from pyauthenticator._user import write_qrcode_to_file, get_two_factor_code, add_two_factor_provider, list_two_factor_providers

__all__ = [
    "write_qrcode_to_file",
    "get_two_factor_code",
    "add_two_factor_provider",
    "list_two_factor_providers",
]
__version__: str = _version.__version__
