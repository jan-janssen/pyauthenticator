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
Add new service
```
pyauthenticator --add /path/to/qrcode.png <service name>
```

Generate authentication code
```
pyauthenticator <service name>
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
The configuration is stored in `~/.pyauthenticator` it is written in the JSON format. For a given service like `github`
the config file contains:
```
{"github": "otpauth://totp/GitHub:<username>?secret=<secret>&issuer=GitHub"}
```
With the github username `<username>` and the corresponding secret `<secret>` contained in the QR code