"""
Configuration file handling for pyauthenticator
"""

import json
from os.path import exists, abspath, expanduser
from typing import Any, Dict

# default configuration file
default_config_file: str = "~/.pyauthenticator"


def load_config(config_file_to_load: str = default_config_file) -> Dict[str, Any]:
    """
    Load configuration file

    Args:
        config_file_to_load (str): path to config file

    Returns:
        dict: Dictionary with service names as keys and the otpauth url as values
    """
    abs_config_path = abspath(expanduser(config_file_to_load))
    if exists(abs_config_path):
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
    with open(abspath(expanduser(config_file_to_write)), "w") as f:
        json.dump(config_dict, f)
