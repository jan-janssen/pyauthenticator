"""
Generate two factor authentication codes on the command line
"""
import argparse
from pyauthenticator.share import (
    list_services,
    load_config,
    generate_qrcode,
    add_service,
    get_two_factor_code,
)


def command_line_parser():
    """
    Main function primarly used for the command line interface
    """
    parser = argparse.ArgumentParser(prog="pyauthenticator")
    config_dict = load_config()
    parser.add_argument(
        "service",
        help="Service to generate optauth code for. Available services are: "
             + str(list_services(config_dict=config_dict)),
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
        help="Add service by providing the qrcode png file as additional argument.",
    )
    args = parser.parse_args()
    if args.qrcode:
        generate_qrcode(key=args.service, config_dict=config_dict)
    elif args.add:
        add_service(
            key=args.service, qrcode_png_file_name=args.add, config_dict=config_dict
        )
        print(args.service, "added.")
    else:
        print(get_two_factor_code(key=args.service, config_dict=config_dict))
