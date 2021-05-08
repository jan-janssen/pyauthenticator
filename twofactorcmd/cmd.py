import argparse
import base64
import json
import os
from otpauth import OtpAuth
import qrcode


config_file = "~/.twofactorcmd"


def load_config():
    abs_config_path = os.path.abspath(
        os.path.expanduser(
            config_file
        )
    )
    with open(abs_config_path, "r") as f:
        return json.load(f)


def get_otpauth_dict(otpauth_str):
    return {
        kv[0]: kv[1]
        for kv in [
            otpvar.split("=")
            for otpvar in otpauth_str.replace("?", "&").split("&")[1:]
        ]
    }


def add_padding(main_str, padding_str, padding_length, inverse_padding=False):
    missing_padding = len(main_str) % padding_length
    if missing_padding:
        if inverse_padding:
            main_str = padding_str * (padding_length - missing_padding) + main_str
        else:
            main_str += padding_str * (padding_length - missing_padding)
    return main_str


def init_auth(otpauth_secret):
    return OtpAuth(
        secret=base64.b32decode(
            add_padding(
                main_str=otpauth_secret,
                padding_str='=',
                padding_length=8,
                inverse_padding=False
            ),
            True
        )
    )


def check_if_key_in_config(key, config_dict):
    if key not in config_dict.keys():
        raise ValueError()


def get_two_factor_code(key, config_dict):
    check_if_key_in_config(
        key=key,
        config_dict=config_dict
    )
    decode_dict_internal = get_otpauth_dict(
        otpauth_str=config_dict[key]
    )
    auth = init_auth(
        otpauth_secret=decode_dict_internal["secret"]
    )
    if "period" in decode_dict_internal.keys():
        auth_code = auth.totp(
            period=int(
                decode_dict_internal['period']
            )
        )
    else:
        auth_code = auth.totp()
    return add_padding(
        main_str=str(auth_code),
        padding_str="0",
        padding_length=6,
        inverse_padding=True
    )


def generate_qrcode(key, config_dict, file_name=None):
    if file_name is None:
        file_name = key + ".png"
    check_if_key_in_config(
        key=key,
        config_dict=config_dict
    )
    qrcode.make(config_dict[key]).save(
        file_name,
        "PNG"
    )


def list_services(config_dict):
    return config_dict.keys()


def main():
    parser = argparse.ArgumentParser(prog="twofactorcmd")
    parser.add_argument(
        "service",
        help="Service to generate optauth code for. Available services are: "
             + str([s for s in list_services(config_dict=load_config())])
    )
    parser.add_argument(
        "--qrcode",
        help="Generate qrcode as <service.png> file."
    )
    args = parser.parse_args()
    if args.qrcode:
        generate_qrcode(key=args.service, config_dict=load_config())
    else:
        print(
            get_two_factor_code(
                key=args.service,
                config_dict=load_config()
            )
        )


if __name__ == "__main__":
    main()
