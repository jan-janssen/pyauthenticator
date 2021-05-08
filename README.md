# pyauthenticator
Similar to the Google authenticator just written in Python. With more and more services requiring two factor
authentication without supporting application specific passwords or other forms of token based authenication
suitable for automation this python packages allows to generate two factor authentication codes on the commandline
or in python.

## Installation
Install via pip
```
pip install git+https://github.com/jan-janssen/pyauthenticator.git
```

## Command Line
Generate authentication code
```
pyauthenticator <service>
```

Get help and a list of all available services:
```
pyauthenticator -h
```

## Python Interface
Use python interface
```
from pyauthenticator import get_two_factor_code
get_two_factor_code(service)
```

## Configuration
The configuration is stored in `~/.twofactorcmd` it is written in the JSON format. For a given service like `github` the
config file can be created like this:
```
import json
import os

config_file = os.path.expanduser("~/.twofactorcmd")
config_content = {
    "github": "otpauth://totp/GitHub:<username>?secret=<secret>&issuer=GitHub",
}

with open(config_file, "w") as f:
    json.dump(config_content, f)
```
Replace `<username>` and `<secret>` with your user details, which are included in the QR code.

## Convert QRcodes
To extract the optauth url from an qrcode use:
```
from pyzbar.pyzbar import decode
from PIL import Image

file_name = "qrcode.png"
print(decode(Image.open(file_name))[0].data.decode("utf-8"))
```