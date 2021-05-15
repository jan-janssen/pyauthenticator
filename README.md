# pyauthenticator
[![Coverage Status](https://coveralls.io/repos/github/jan-janssen/pyauthenticator/badge.svg?branch=master)](https://coveralls.io/github/jan-janssen/pyauthenticator?branch=master)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Similar to the Google authenticator just written in Python. With more and more services requiring two factor
authentication without supporting application specific passwords or other forms of token based authenication
suitable for automation this python packages allows to generate two factor authentication codes on the commandline
or in python.

## Installation
Install via conda:
```
conda install -c conda-forge pyauthenticator
```

Install via pip:
```
pip install pyauthenticator
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