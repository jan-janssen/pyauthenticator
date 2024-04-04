"""
Shared functionality to generate two factor authentication codes
"""

import json
import os
from inspect import signature

import pyotp
import qrcode
from PIL import Image
from pyzbar.pyzbar import decode

# default configuration file
config_file = "~/.pyauthenticator"


def expand_path(path):
    """
    Expand path by expanding the user variable and converting the path to an absolute path

    Args:
        path (str): path before expansion

    Returns:
        str: expanded path
    """
    return os.path.abspath(os.path.expanduser(path))


def load_config(config_file_to_load=config_file):
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


def write_config(config_dict, config_file_to_write=config_file):
    """
    Write configuration file

    Args:
        config_dict (dict): configuration dictionary
        config_file_to_write (str): path to config file
    """
    with open(expand_path(path=config_file_to_write), "w") as f:
        json.dump(config_dict, f)


def get_otpauth_dict(otpauth_str):
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


def check_if_key_in_config(key, config_dict):
    """
    Check if a given key is included in a dictionary, raise an ValueError if it is not.

    Args:
        key (str): key as string
        config_dict (dict): configuration dictionary
    """
    if key not in config_dict.keys():
        raise ValueError()


def get_two_factor_code(key, config_dict):
    """
    Generate the two factor authentication code

    Args:
        key (str): lower case name of the service
        config_dict (dict): configuration dictionary

    Returns:
        str: two factor authentication code as string
    """
    check_if_key_in_config(key=key, config_dict=config_dict)
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
    key, qrcode_png_file_name, config_dict, config_file_to_write=config_file
):
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


def generate_qrcode(key, config_dict, file_name=None):
    """
    Write qrcode to file to scan it with a mobile application

    Args:
        key (str): lower case name of the service
        config_dict (dict): configuration dictionary
        file_name (str/ None): default file name <service.png>
    """
    if file_name is None:
        file_name = key + ".png"
    check_if_key_in_config(key=key, config_dict=config_dict)
    qrcode.make(config_dict[key]).save(file_name, "PNG")


def list_services(config_dict):
    """
    List available services

    Args:
        config_dict (dict): configuration dictionary

    Returns:
        list: list of available services
    """
    return list(config_dict.keys())
