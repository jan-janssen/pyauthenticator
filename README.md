# pyauthenticator
[![Python package](https://github.com/jan-janssen/pyauthenticator/actions/workflows/unittest.yml/badge.svg?branch=main)](https://github.com/jan-janssen/pyauthenticator/actions/workflows/unittest.yml)
[![Coverage Status](https://coveralls.io/repos/github/jan-janssen/pyauthenticator/badge.svg?branch=main)](https://coveralls.io/github/jan-janssen/pyauthenticator?branch=main)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Similar to the Google authenticator just written in Python. With more and more services requiring two factor
authentication without supporting application specific passwords or other forms of token based authenication
suitable for automation this python packages allows to generate two factor authentication codes on the commandline
or in python.

![Preview of pyauthenticator](https://raw.githubusercontent.com/jan-janssen/pyauthenticator/main/pyauthenticator.gif) 

# For Users 
## Installation
Install `pyauthenticator` via conda:
```
>>> conda install -c conda-forge pyauthenticator
```

Alternatively, `pyauthenticator` can also be installed via pip:
```
>>> pip install pyauthenticator
```

## Command Line
Get help how to use `pyauthenticator` using the `--help/-h` option:
```
>>> pyauthenticator --help

usage: pyauthenticator [-h] [-qr] [-a ADD] service

positional arguments:
  service            Service to generate optauth code for. Currently no
                     service is defined in the ~/.pyauthenticator config file.

options:
  -h, --help         show this help message and exit
  -qr, --qrcode      Generate qrcode as <service.png> file.
  -a ADD, --add ADD  Add service by providing the <qrcode.png> file as
                     additional argument.
```

Add `google` as new service after saving the qrcode to `Screenshot 2023-07-02 at 12.45.09.png` to your desktop:
```
>>> pyauthenticator google --add ~/Desktop/Screenshot\ 2023-07-02\ at\ 12.45.09.png

The service 'google' was added, from file </Users/jan/Desktop/Screenshot 2023-07-02 at 12.45.09.png>
```

Afterwards, new authentication codes can be generated for the service `google` using:
```
>>> pyauthenticator google

087078
```
Beyond google, `pyauthenticator` works for any service which implements the two factor authentication. 

If you mistype the name of the service, then `pyauthenticator` suggests alternative options:
```
>>> pyauthenticator googel

The service "googel" does not exist.

The config file ~/.pyauthenticator contains the following services:
  * google

Choose one of these or add a new service using:
  pyauthenticator --add <qr-code.png> <servicename>
```

## Support 
For any support requests feel free to open an [issue on Github](https://github.com/jan-janssen/pyauthenticator/issues). 

# For Developers 
## Python Interface
The same functionality which is available on the command line is also available via the python interface:
```
from pyauthenticator import get_two_factor_code
get_two_factor_code(service)
```
So `pyauthenticator` can be integrated in existing python packages which need access to resources protected by two 
factor authentication. 

## Configuration
The configuration is stored in `~/.pyauthenticator` it is written in the JSON format. For a given service like `github`
the config file contains:
```
{"google": "otpauth://totp/Google:<username>?secret=<secret>&issuer=Google"}
```
With the Google username `<username>` and the corresponding secret `<secret>` being contained in the QR code.

## License 
The `pyauthenticator` package is licensed under the [BSD-3-Clause license](https://github.com/jan-janssen/pyauthenticator/blob/main/LICENSE). 