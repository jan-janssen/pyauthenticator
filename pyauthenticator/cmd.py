#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK
"""
Generate two factor authentication codes on the command line
"""
import argparse
import argcomplete
from argcomplete.completers import ChoicesCompleter
from pyauthenticator.share import (
    list_services,
    load_config,
    generate_qrcode,
    add_service,
    get_two_factor_code,
)


def main():
    """
    Main function primarly used for the command line interface
    """
    parser = argparse.ArgumentParser(prog="pyauthenticator")
    services_lst = tuple(list_services(config_dict=load_config()))
    parser.add_argument(
        "service",
        help="Service to generate optauth code for.",
        choices=services_lst
    ).completer = ChoicesCompleter(services_lst)
    parser.add_argument(
        "-qr",
        "--qrcode",
        action="store_true",
        help="Generate qrcode as <service.png> file.",
    ).completer = ChoicesCompleter(services_lst)
    parser.add_argument(
        "-a",
        "--add",
        help="Add service by providing the qrcode png file as additional argument.",
    )
    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    if args.qrcode:
        generate_qrcode(key=args.service, config_dict=load_config())
    elif args.add:
        add_service(
            key=args.service, qrcode_png_file_name=args.add, config_dict=load_config()
        )
        print(args.service, "added.")
    else:
        print(get_two_factor_code(key=args.service, config_dict=load_config()))


if __name__ == "__main__":
    main()
