# TOTP codes in shell scripts

## Problem

A shell script, cron job, or CI step needs to authenticate against a service that requires a time-based one-time password (TOTP), but there's no interactive user available to read a code off a phone and type it in.

[`pyauthenticator`](https://github.com/jan-janssen/pyauthenticator) stores TOTP credentials locally (imported once from the same QR code used to set up an authenticator app) and prints the current code on demand, so it can be called from any shell script like any other CLI tool.

## Prerequisites

Install `pyauthenticator`:

```bash
pip install pyauthenticator
```

Import the account once, from the QR code shown when the service's two-factor authentication was configured:

```bash
pyauthenticator myservice --add ~/Desktop/myservice-qrcode.png
```

## Capturing a code in a variable

```bash
OTP="$(pyauthenticator myservice)"
echo "Current code: $OTP"
```

## Example: passing a TOTP code to a CLI tool

Many command-line tools accept a one-time password as an argument or header. For example, a REST API that requires a TOTP header on login:

```bash
#!/usr/bin/env bash
set -euo pipefail

TOKEN=$(
  curl -sf -X POST https://example.com/api/login \
    -H "Content-Type: application/json" \
    -H "X-OTP-Code: $(pyauthenticator myservice)" \
    -d '{"username": "me"}' \
  | jq -r '.token'
)

echo "Logged in, token: $TOKEN"
```

Because `pyauthenticator myservice` is only valid for the current 30-second TOTP window, generate it inline (as above) right before it's used, rather than reusing a value captured earlier in a long-running script.

## Example: waiting out an expiring code

If a script runs close to a 30-second window boundary, a code generated a moment too early can expire before it reaches the server. A simple retry loop makes this robust without needing to know the exact TOTP period:

```bash
#!/usr/bin/env bash
set -euo pipefail

attempt_login() {
    curl -sf -X POST https://example.com/api/login \
        -H "X-OTP-Code: $(pyauthenticator myservice)" \
        -d '{"username": "me"}'
}

for attempt in 1 2 3; do
    if attempt_login; then
        exit 0
    fi
    echo "Login attempt $attempt failed, retrying..." >&2
    sleep 2
done

echo "Login failed after 3 attempts" >&2
exit 1
```

## Related recipes

* [Automating SSH logins that require a password and a TOTP code](ssh-askpass.md) — a more specific case where the OTP is one of two prompts `ssh` itself needs answered.
* [Generating TOTP codes from Python](python-totp.md) — the same functionality from a Python script instead of the shell.

## Security considerations

Storing and using a TOTP secret from an automated script removes the "something you have, checked by a human" property that two-factor authentication is meant to provide. Only automate TOTP entry when this is consistent with the target service's and organization's policies, and prefer a dedicated automation credential (API token, application password, service account) when one is available. See the [security considerations in the README](https://github.com/jan-janssen/pyauthenticator#security-considerations) for more detail.
