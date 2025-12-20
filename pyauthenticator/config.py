"""
Shared functionality to generate two factor authentication codes
"""

import json
import os
from typing import Any, Dict

# default configuration file
default_config_file: str = "~/.pyauthenticator"


def expand_path(path: str) -> str:
    """
    Expand path by expanding the user variable and converting the path to an absolute path

    Args:
        path (str): path before expansion

    Returns:
        str: expanded path
    """
    return os.path.abspath(os.path.expanduser(path))


def load_config(config_file_to_load: str = default_config_file) -> Dict[str, Any]:
    """
    Load configuration file

    Args:
        config_file_to_load (str): path to config file

    Returns:
        dict: Dictionary with service names as keys and the otpauth url as values
    """
    abs_config_path = expand_path(path=config_file_to_load)
    if os.path.exists(abs_config_path):
        with open(abs_config_path, "r") as f:
            return json.load(f)
    else:
        return {}


def write_config(
    config_dict: Dict[str, Any], config_file_to_write: str = default_config_file
) -> None:
    """
    Write configuration file

    Args:
        config_dict (dict): configuration dictionary
        config_file_to_write (str): path to config file
    """
    with open(expand_path(path=config_file_to_write), "w") as f:
        json.dump(config_dict, f)


def get_otpauth_dict(otpauth_str: str) -> Dict[str, str]:
    """
    Parse otpauth url

    Args:
        otpauth_str (str): otpauth url as string

    Returns:
        dict: Dictionary with the parameters of the otpauth url as key-value pairs
    """
    return {
        kv[0]: kv[1]
        for kv in [
            otpvar.split("=") for otpvar in otpauth_str.replace("?", "&").split("&")[1:]
        ]
    }
