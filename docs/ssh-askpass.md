# Automating SSH logins

## Problem

Some SSH servers are configured with two-factor authentication: after the password prompt, the server (typically via a PAM module) asks for a second, time-based one-time password (TOTP) — often shown as a prompt like `Your OTP:` or `Verification code:`. Tools that automate SSH sessions (batch jobs, `rsync` wrappers, CI runners, IDE remote hosts) normally only handle the password prompt, so a second interactive prompt breaks them.

OpenSSH already has a mechanism for answering prompts non-interactively: `SSH_ASKPASS`. This page shows a complete, working setup that answers both prompts — the password from a local secret store and the OTP from [`pyauthenticator`](https://github.com/jan-janssen/pyauthenticator) — without any manual typing.

## How `SSH_ASKPASS` works

When `ssh` needs to ask the user something and cannot use the controlling terminal (or `SSH_ASKPASS_REQUIRE` forces it), it runs the program named by the `SSH_ASKPASS` environment variable and passes the prompt text as its first argument. Whatever that program prints to stdout is used as the answer.

Two environment variables control this:

* `SSH_ASKPASS` — path to an executable that receives the prompt as `$1` and prints the answer.
* `SSH_ASKPASS_REQUIRE=force` — makes `ssh` use `SSH_ASKPASS` even when run from an interactive terminal (without this, `ssh` normally only uses it when there is no terminal available, e.g. when launched from a GUI).

Because the helper program receives the *prompt text*, a single script can distinguish a password prompt from an OTP prompt and answer each differently.

## Prerequisites

1. Install `pyauthenticator`:

   ```bash
   pip install pyauthenticator
   ```

2. Import the TOTP secret once, from the QR code your SSH provider/computing centre gave you when enrolling your authenticator app:

   ```bash
   pyauthenticator myserver --add ~/Desktop/myserver-qrcode.png
   ```

   From then on, `pyauthenticator myserver` prints the current 6-digit code.

## Complete example

Create `~/.ssh/askpass-helper.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

PROMPT="${1:-}"

case "$PROMPT" in
    *"'s password:"*)
        # Retrieve the password from a secure credential store, e.g. the
        # macOS keychain:
        #   security find-generic-password -s myserver -w
        # or a password manager's CLI (1Password `op`, `pass`, etc.).
        security find-generic-password -s myserver -w
        ;;

    *"Your OTP:"*|*"Verification code:"*)
        # Generate the current TOTP code for the "myserver" account.
        exec pyauthenticator myserver
        ;;

    *)
        echo "Unexpected SSH prompt: $PROMPT" >&2
        exit 1
        ;;
esac
```

Make it executable:

```bash
chmod +x ~/.ssh/askpass-helper.sh
```

Then export the two environment variables, for example in `~/.bashrc` or `~/.zshrc`:

```bash
export SSH_ASKPASS="$HOME/.ssh/askpass-helper.sh"
export SSH_ASKPASS_REQUIRE=force
```

Open a new shell (or `source` the file) and connect as usual:

```bash
ssh myserver
```

`ssh` now calls `askpass-helper.sh` for the password prompt and again for the OTP prompt, and the connection completes without any manual input.

## Adjusting the prompt text

The `case` statement matches on the literal prompt text, which depends on the SSH server and PAM module configuration of the target system. `'s password:` is the standard OpenSSH password prompt (preceded by the username). `Your OTP:` and `Verification code:` are common phrasings for PAM-based TOTP modules (e.g. `pam_oath`, `google-authenticator`), but the exact wording varies by system. Run `ssh -v myserver` once to see the literal prompt text logged, and adjust the `case` patterns accordingly.

## Security considerations

This setup removes the human-in-the-loop step that two-factor authentication is designed to provide: the password and the TOTP secret both end up readable by an automated process on the same machine. Some organizations and computing centres explicitly prohibit this kind of automation.

**Only set this up when it is consistent with the security policies of the systems and organizations you connect to.** Check with the relevant administrators or computing centre first, and prefer a dedicated automation credential (an SSH key, an API token, a service account) whenever the target system offers one — see [Generating TOTP codes from Python](python-totp.md) and the [security considerations in the README](https://github.com/jan-janssen/pyauthenticator#security-considerations) for more on when TOTP automation is and isn't appropriate.
