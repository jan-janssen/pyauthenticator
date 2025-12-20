"""
Generate two factor authentication codes on the command line
"""

import argparse
import sys
from typing import Optional, Sequence

from pyauthenticator._config import load_config
from pyauthenticator.api import (
    add_service,
    generate_qrcode,
    get_totp_for_key_in_dict,
    list_services,
)


def command_line_parser(cmd_args: Optional[Sequence[str]] = None) -> None:
    """
    Main function primarly used for the command line interface
    """
    if cmd_args is None:
        cmd_args = sys.argv[1:]
    parser = argparse.ArgumentParser(prog="pyauthenticator")
    config_dict = load_config()
    if len(config_dict) > 0:
        parser.add_argument(
            "service",
            help="Service to generate optauth code for. The config file ~/.pyauthenticator contains the following services: "
            + ", ".join(list_services(config_dict=config_dict)),
        )
    else:
        parser.add_argument(
            "service",
            help="Service to generate optauth code for. Currently no service is defined in the ~/.pyauthenticator config file.",
        )
    parser.add_argument(
        "-qr",
        "--qrcode",
        action="store_true",
        help="Generate qrcode as <service.png> file.",
    )
    parser.add_argument(
        "-a",
        "--add",
        help="Add service by providing the <qrcode.png> file as additional argument.",
    )
    args = parser.parse_args(args=cmd_args)
    if args.qrcode:
        try:
            generate_qrcode(key=args.service, config_dict=config_dict)
        except KeyError:
            _print_service_does_not_exists(config_dict=config_dict, service=args.service)
        else:
            print("The qrcode file <" + args.service + ".png> was generated.")
    elif args.add:
        add_service(
            key=args.service, qrcode_png_file_name=args.add, config_dict=config_dict
        )
        print(
            "The service '"
            + args.service
            + "' was added, from file <"
            + args.add
            + ">."
        )
    else:
        try:
            print(get_totp_for_key_in_dict(key=args.service, config_dict=config_dict))
        except KeyError:
            _print_service_does_not_exists(config_dict=config_dict, service=args.service)


def _print_service_does_not_exists(config_dict: dict, service: str) -> None:
    if len(config_dict) > 0:
        print(
            'The service "'
            + service
            + '" does not exist.\n\nThe config file ~/.pyauthenticator contains the following services:'
        )
        for service_in_config in list_services(config_dict=config_dict):
            print("  * " + service_in_config)
        print("\nChoose one of these or add a new service using:")
    else:
        print(
            "The config file ~/.pyauthenticator does not contain any services. To add a new service use:"
        )
    print("  pyauthenticator --add <qr-code.png> <servicename>\n")


if __name__ == "__main__":
    command_line_parser()
