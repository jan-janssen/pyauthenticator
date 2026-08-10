# MCP agent for TOTP codes

## Problem

An AI agent connected through [MCP](https://modelcontextprotocol.io/) (for example Claude Desktop, or another MCP-compatible host) is asked to carry out a task that involves logging into a service protected by two-factor authentication — filling in a web form, calling an API, or completing an SSH session — and needs a valid TOTP code to do so, without a person relaying it manually.

[`pyauthenticator`](https://github.com/jan-janssen/pyauthenticator) ships an MCP server that exposes the same local TOTP credential store used by its command-line and Python interfaces as a small set of MCP tools.

## Installation

```bash
pip install "pyauthenticator[mcp]"
```

This installs the `pyauthenticator-mcp` executable, requires Python 3.10+.

## Configuration

Find the absolute path to the installed executable:

```bash
which pyauthenticator-mcp
```

Using an absolute path is recommended because desktop applications commonly start MCP servers without loading the environment configuration of an interactive shell.

Add it to the host's MCP server configuration, for example:

```json
{
  "mcpServers": {
    "pyauthenticator": {
      "command": "/absolute/path/to/pyauthenticator-mcp"
    }
  }
}
```

### Claude Desktop

Claude Desktop stores its MCP configuration in `claude_desktop_config.json`, accessible via **Settings → Developer → Edit Config**. Typical locations:

* macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
* Windows: `%APPDATA%\Claude\claude_desktop_config.json`
* Linux: `~/.config/Claude/claude_desktop_config.json`

Only add or modify the `mcpServers` entry needed for `pyauthenticator`; leave unrelated settings unchanged:

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

Restart Claude Desktop after editing the file.

## Available tools

| Tool | Arguments | Description |
| --- | --- | --- |
| `get_code` | `service: str` | Generate a two-factor authentication code for a configured service. |
| `list_services` | – | List configured service names. |
| `add_service` | `service: str`, `qrcode_path: Optional[str]`, `qrcode_base64: Optional[str]` | Add a service from a QR-code file or base64-encoded PNG. |
| `remove_service` | `service: str` | Remove a configured service. |
| `get_qrcode` | `service: str` | Return the QR code for a configured service as an MCP image. |

`get_code`, `remove_service`, and `get_qrcode` report the currently configured services when the requested service does not exist, so an agent can recover from a typo by listing what's available.

## Example interaction

Once configured, an agent can be asked directly, e.g.:

> "Log into the staging dashboard and check the last deploy status. The two-factor code is under the service name `staging`."

The agent calls `list_services` to confirm `staging` exists (or `add_service` first, if a QR code needs to be imported), then `get_code("staging")` to retrieve the current code at the point it's needed in the login flow.

## Shared configuration

The MCP server reads and writes the same `~/.pyauthenticator` configuration file as the command-line and Python interfaces. A service added through the CLI (`pyauthenticator myservice --add ...`) is immediately visible to `list_services`, and vice versa — see [Using TOTP codes in shell scripts and CLI workflows](shell-automation.md) and [Generating TOTP codes from Python](python-totp.md).

## Security considerations

Exposing `get_code` to an agent gives that agent — and anything that can direct its actions — the ability to generate valid two-factor codes on demand. Only configure this for services and organizations where automated TOTP use is permitted, be deliberate about which services are imported into the shared configuration file, and treat `~/.pyauthenticator` like any other credential file. See the [security considerations in the README](https://github.com/jan-janssen/pyauthenticator#security-considerations) for more detail.
