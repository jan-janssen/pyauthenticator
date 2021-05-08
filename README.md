# Two Factor CMD
With more and more services requiring two factor authentication without supporting application specific passwords or
other forms of token based authenication suitable for automation this python packages allows to generate two factor
authentication codes on the commandline or in python.

## Installation
Install via pip
```
pip install git+https://github.com/jan-janssen/twofactorcmd.git
```

## Command Line
Generate authentication code
```
twofactorcmd <service>
```

Get help and a list of all available services:
```
twofactorcmd -h
```

## Python Interface
Use python interface
```
from twofactorcmd import get_two_factor_code
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