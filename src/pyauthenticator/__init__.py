"""
Generate two factor authentication codes on the command line
"""

from pyauthenticator._user import (
    add_two_factor_provider,
    get_two_factor_code,
    list_two_factor_providers,
    write_qrcode_to_file,
)

from . import _version

__all__ = [
    "write_qrcode_to_file",
    "get_two_factor_code",
    "add_two_factor_provider",
    "list_two_factor_providers",
]
__version__: str = _version.__version__
