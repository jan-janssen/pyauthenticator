# pyauthenticator

[![Pipeline](https://github.com/jan-janssen/pyauthenticator/actions/workflows/pipeline.yml/badge.svg)](https://github.com/jan-janssen/pyauthenticator/actions/workflows/pipeline.yml)
[![codecov](https://codecov.io/github/jan-janssen/pyauthenticator/graph/badge.svg?token=K0VG71K9YI)](https://codecov.io/github/jan-janssen/pyauthenticator)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**TOTP authentication for Python, the command line, and automation.**

`pyauthenticator` provides a lightweight way to manage and generate time-based one-time passwords (TOTP) from scripts, Python applications, command-line workflows, and MCP clients.

It is particularly useful when a service requires two-factor authentication but does not provide application-specific passwords, API tokens, or another authentication mechanism suitable for automation.

Once an account has been imported from its authenticator QR code, generating a code is as simple as:

```bash
pyauthenticator github
```

or from Python:

```python
from pyauthenticator import get_two_factor_code

code = get_two_factor_code("github")
```

![Preview of pyauthenticator](https://raw.githubusercontent.com/jan-janssen/pyauthenticator/main/pyauthenticator.gif)

## Why pyauthenticator?

Libraries such as [PyOTP](https://github.com/pyauth/pyotp) provide the underlying HOTP/TOTP algorithms for Python applications. `pyauthenticator` builds on PyOTP and focuses instead on **managing and consuming TOTP credentials for automation**.

|                                   | PyOTP                        | pyauthenticator                             |
| --------------------------------- | ---------------------------- | ------------------------------------------- |
| Generate TOTP/HOTP codes          | ✅                           | ✅                                          |
| Verify OTP codes                  | ✅                           | —                                           |
| Parse `otpauth://` URIs           | ✅                           | ✅                                          |
| Manage named accounts             | —                            | ✅                                          |
| Import authenticator QR codes     | —                            | ✅                                          |
| Persistent local credential store | —                            | ✅                                          |
| Command-line interface            | —                            | ✅                                          |
| High-level Python interface       | —                            | ✅                                          |
| MCP server                        | —                            | ✅                                          |
| Primary use case                  | Implement OTP authentication | Use existing TOTP credentials in automation |

In short:

* **Use PyOTP** when implementing OTP authentication inside an application.
* **Use pyauthenticator** when you already have TOTP credentials and want to access them conveniently from Python, the shell, SSH automation, or other tools.

## Installation

Install `pyauthenticator` from conda-forge:

```bash
conda install -c conda-forge pyauthenticator
```

or from PyPI:

```bash
pip install pyauthenticator
```

## Quick start

### Add an account

Save the QR code normally shown when configuring an authenticator application.

For example, if the QR code is stored as:

```text
~/Desktop/github-qrcode.png
```

add it as the service `github`:

```bash
pyauthenticator github --add ~/Desktop/github-qrcode.png
```

`pyauthenticator` extracts the `otpauth://` credential from the QR code and stores it locally.

### Generate a TOTP code

After adding the service:

```bash
pyauthenticator github
```

returns the current authentication code:

```text
087078
```

`pyauthenticator` works with services using standard TOTP authentication, not only Google accounts.

## Command-line interface

Display the available options with:

```bash
pyauthenticator --help
```

Example output:

```text
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

### Import an account

For example:

```bash
pyauthenticator google --add ~/Desktop/google-qrcode.png
```

### Generate a code

```bash
pyauthenticator google
```

### Export a QR code

The QR code associated with a configured service can be generated with:

```bash
pyauthenticator google --qrcode
```

### Service-name suggestions

If a service name is mistyped, `pyauthenticator` lists the configured services and suggests alternatives:

```bash
pyauthenticator googel
```

For example:

```text
The service "googel" does not exist.

The config file ~/.pyauthenticator contains the following services:
  * google

Choose one of these or add a new service using:
  pyauthenticator --add <qr-code.png> <servicename>
```

## Using pyauthenticator for automation

The command-line interface makes TOTP codes directly available to shell scripts and other programs.

For example:

```bash
TOKEN="$(pyauthenticator github)"
```

The resulting value can then be passed to another process which requires a TOTP code.

This makes `pyauthenticator` useful for workflows such as:

* shell scripts,
* SSH authentication helpers,
* automated command-line applications,
* Python workflows,
* developer tools,
* MCP-compatible agents.

Whenever possible, dedicated API tokens, application passwords, SSH keys, OAuth credentials, or other machine-oriented authentication mechanisms should be preferred. `pyauthenticator` is intended for situations where a service requires TOTP authentication and no more suitable automation interface is available.

## Python interface

The same functionality is available through Python:

```python
from pyauthenticator import get_two_factor_code

code = get_two_factor_code("github")
```

This allows existing Python applications and workflows to access services protected by TOTP authentication without reimplementing credential loading or OTP generation.

## Configuration

Configured services are stored in:

```text
~/.pyauthenticator
```

The configuration uses JSON. A configured service contains the `otpauth://` URI extracted from the corresponding QR code.

For example:

```json
{
  "google": "otpauth://totp/Google:<username>?secret=<secret>&issuer=Google"
}
```

The URI contains the TOTP secret required to generate authentication codes.

## Security considerations

The TOTP secret stored by `pyauthenticator` is an authentication credential. Anyone who can obtain this secret can generate the same one-time passwords.

The local `~/.pyauthenticator` configuration should therefore be treated like other sensitive credential files.

Using TOTP from an automated process also changes the traditional security model of two-factor authentication: the password and second-factor secret may ultimately become accessible from the same machine.

For automated access, prefer mechanisms explicitly designed for machine authentication whenever the target service provides them, such as:

* API tokens,
* application-specific passwords,
* SSH keys,
* OAuth credentials,
* service accounts.

`pyauthenticator` is intended primarily for services where TOTP authentication is required and no suitable machine-oriented alternative exists.

## MCP server

`pyauthenticator` also provides an MCP server for MCP-compatible hosts on Python 3.10+.

Install the optional MCP dependency with:

```bash
pip install "pyauthenticator[mcp]"
```

The server is exposed through:

```bash
pyauthenticator-mcp
```

The MCP server uses the same `~/.pyauthenticator` configuration as the command-line and Python interfaces. Services added through one interface are therefore immediately available through the others.

### Example MCP configuration

An MCP-compatible host can launch the server using a configuration such as:

```json
{
  "mcpServers": {
    "pyauthenticator": {
      "command": "/absolute/path/to/pyauthenticator-mcp"
    }
  }
}
```

Using an absolute path is recommended because desktop applications commonly start MCP servers without loading the environment configuration of an interactive shell.

If `pyauthenticator-mcp` is installed inside a conda environment or virtual environment, find the executable with:

```bash
which pyauthenticator-mcp
```

and use the resulting path in the MCP configuration.

### Claude Desktop configuration

Claude Desktop stores its MCP configuration in `claude_desktop_config.json`.

Typical locations are:

* macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
* Windows: `%APPDATA%\Claude\claude_desktop_config.json`
* Linux: `~/.config/Claude/claude_desktop_config.json`

In Claude Desktop, the configuration can also be accessed through **Settings → Developer → Edit Config**.

Only add or modify the `mcpServers` entry needed for `pyauthenticator`; leave unrelated settings unchanged.

For example:

```json
{
  "mcpServers": {
    "pyauthenticator": {
      "command": "/Users/<you>/mambaforge/bin/pyauthenticator-mcp"
    }
  },
  "preferences": {
    "...": "..."
  }
}
```

### Available MCP tools

| Tool             | Arguments                                                                    | Description                                                         |
| ---------------- | ---------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `get_code`       | `service: str`                                                               | Generate a two-factor authentication code for a configured service. |
| `list_services`  | –                                                                            | List configured service names.                                      |
| `add_service`    | `service: str`, `qrcode_path: Optional[str]`, `qrcode_base64: Optional[str]` | Add a service from a QR-code file or base64-encoded PNG.            |
| `remove_service` | `service: str`                                                               | Remove a configured service.                                        |
| `get_qrcode`     | `service: str`                                                               | Return the QR code for a configured service as an MCP image.        |

`get_code`, `remove_service`, and `get_qrcode` report the currently configured services when the requested service does not exist, mirroring the command-line behavior.

## Use cases

`pyauthenticator` is intended as a small bridge between TOTP authentication and automation.

Typical applications include:

### Command-line workflows

```bash
pyauthenticator myservice
```

### Shell scripts

```bash
OTP="$(pyauthenticator myservice)"
```

### Python applications

```python
from pyauthenticator import get_two_factor_code

otp = get_two_factor_code("myservice")
```

### SSH and remote-system automation

`pyauthenticator` can be combined with tools such as `SSH_ASKPASS` when an SSH service requires a password followed by a TOTP code.

### Agent and MCP workflows

The optional MCP server exposes configured TOTP credentials to MCP-compatible applications while retaining the same local credential store used by the CLI and Python interfaces.

## Support

Questions, bug reports, feature requests, and integration examples are welcome through the [GitHub issue tracker](https://github.com/jan-janssen/pyauthenticator/issues).

Contributions that improve automation workflows, integrations, platform support, documentation, or credential handling are particularly welcome.

## License

`pyauthenticator` is licensed under the [BSD-3-Clause license](https://github.com/jan-janssen/pyauthenticator/blob/main/LICENSE).
