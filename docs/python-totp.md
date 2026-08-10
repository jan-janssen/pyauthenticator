# TOTP codes for Python

## Problem

A Python application, script, or test suite needs to authenticate against a service protected by time-based one-time passwords (TOTP), without a person available to read a code off an authenticator app and type it in — for example an integration test that logs into a real staging environment, or a browser-automation script (Selenium/Playwright) driving a login form that has a TOTP step.

[`pyauthenticator`](https://github.com/jan-janssen/pyauthenticator) stores TOTP credentials locally (imported once from the same QR code used to set up an authenticator app) and exposes them through a small Python API, so a script can request the current code the same way it would read any other local configuration.

## Prerequisites

Install `pyauthenticator`:

```bash
pip install pyauthenticator
```

Import the account once, from the QR code shown when the service's two-factor authentication was configured:

```bash
pyauthenticator myservice --add ~/Desktop/myservice-qrcode.png
```

This can also be done from Python, see [Adding an account from Python](#adding-an-account-from-python) below.

## Generating a code

```python
from pyauthenticator import get_two_factor_code

code = get_two_factor_code("myservice")
print(code)  # e.g. "087078"
```

`get_two_factor_code()` always returns the code valid for the current 30-second TOTP window, so call it immediately before using the result rather than caching it.

## Example: logging into a web form with Playwright

```python
from playwright.sync_api import sync_playwright

from pyauthenticator import get_two_factor_code

with sync_playwright() as playwright:
    browser = playwright.chromium.launch()
    page = browser.new_page()
    page.goto("https://example.com/login")

    page.fill("#username", "me")
    page.fill("#password", "...")
    page.click("#submit")

    # Generate the OTP right before it's needed, since it is only valid
    # for a short, fixed window.
    page.fill("#otp", get_two_factor_code("myservice"))
    page.click("#verify")

    browser.close()
```

## Example: an integration test fixture

```python
import pytest

from pyauthenticator import get_two_factor_code

from myapp.client import Client


@pytest.fixture
def authenticated_client():
    client = Client(base_url="https://staging.example.com")
    client.login(username="ci-bot", password="...", otp=get_two_factor_code("myservice"))
    return client


def test_something(authenticated_client):
    assert authenticated_client.get("/me").status_code == 200
```

## Adding an account from Python

Accounts can also be imported and managed without going through the command line:

```python
from pyauthenticator import add_two_factor_provider, list_two_factor_providers

add_two_factor_provider("myservice", "/path/to/myservice-qrcode.png")
print(list_two_factor_providers())  # ["myservice"]
```

All three interfaces — Python, the command line, and the [MCP server](mcp.md) — read and write the same local configuration file (`~/.pyauthenticator`), so an account added from one is immediately available from the others.

## Related recipes

* [Using TOTP codes in shell scripts and CLI workflows](shell-automation.md) — the same functionality from the command line instead of Python.
* [Automating SSH logins that require a password and a TOTP code](ssh-askpass.md) — feeding a generated code to `ssh` via `SSH_ASKPASS`.

## Security considerations

`get_two_factor_code()` returns a valid, live authentication credential. Only automate TOTP entry when this is consistent with the target service's and organization's policies, and prefer a dedicated automation credential (API token, application password, service account) when the target system provides one. See the [security considerations in the README](https://github.com/jan-janssen/pyauthenticator#security-considerations) for more detail.
