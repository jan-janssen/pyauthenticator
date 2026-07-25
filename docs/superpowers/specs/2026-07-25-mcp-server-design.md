# MCP Server for pyauthenticator — Design

Date: 2026-07-25

## Motivation

`pyauthenticator` currently exposes its functionality via a CLI and a plain
Python API (`pyauthenticator.get_two_factor_code`, etc.). As AI coding agents
and automation tools increasingly need to drive logins that are protected by
two-factor authentication, the natural integration point for those agents is
the Model Context Protocol (MCP), not shelling out to the CLI or importing
the library directly. This adds a dedicated MCP server so any MCP-compatible
host (Claude Desktop, Claude Code, etc.) can call pyauthenticator as a tool
provider.

Scope decisions made during brainstorming:
- Full CLI parity (add / remove / list / get), not a read-only subset.
- No audit logging or human-in-the-loop gating in this version — the server
  behaves as a transparent wrapper, same trust model as calling the CLI or
  Python API directly today.
- stdio transport only — no network-reachable mode. This does not solve the
  "secret store lives on the same device as the automation" problem raised
  during the initial improvement discussion; it is explicitly out of scope
  for this iteration and left as a future direction.
- The MCP SDK is an optional dependency, not a core one.

## Architecture

- New module `pyauthenticator/mcp_server.py`, built on
  `mcp.server.fastmcp.FastMCP`.
- The module is a thin adapter only. All actual logic (config load/write,
  TOTP generation, QR decode/encode) stays in `pyauthenticator/share.py`,
  which already has test coverage and is used by the CLI. The MCP module
  registers `@mcp.tool()`-decorated functions that call into `share.py` and
  translate results/errors into MCP responses.
- New console-script entry point `pyauthenticator-mcp`
  (`pyauthenticator.mcp_server:main`), so a host config can reference a
  plain command rather than a `python -m` invocation.
- Runs stdio-only, launched as a subprocess by the MCP host. Same machine,
  same `~/.pyauthenticator` config file the CLI already reads/writes. No new
  network surface is introduced.

## Tools exposed

| Tool | Signature | Delegates to |
|---|---|---|
| `get_code` | `(service: str) -> str` | `share.get_two_factor_code` |
| `list_services` | `() -> list[str]` | `share.list_services` |
| `add_service` | `(service: str, qrcode_path: str \| None = None, qrcode_base64: str \| None = None) -> str` | `share.add_service` (extended) |
| `remove_service` | `(service: str) -> str` | new `share.remove_service` |
| `get_qrcode` | `(service: str) -> Image` | `share.generate_qrcode` (adapted) |

### `add_service`

Exactly one of `qrcode_path` or `qrcode_base64` must be provided; passing
both or neither raises `ValueError("Provide exactly one of qrcode_path or
qrcode_base64")`.

Since MCP tool arguments are JSON and have no native binary type,
`qrcode_base64` is a base64-encoded string of PNG bytes (this is documented
in the tool's description so a calling agent knows to encode it). Internally
the base64 string is decoded to bytes and wrapped in
`PIL.Image.open(io.BytesIO(...))`.

To support both the file-path and bytes cases without duplicating the QR
decode logic, `share.add_service` is refactored to accept an already-open
`PIL.Image` object as its core operation; the existing file-path call becomes
a thin wrapper that opens the file and delegates to it. This is a targeted
refactor of code the MCP feature directly depends on, not unrelated cleanup.

### `remove_service`

New addition to `share.py`, matching the existing style of the module:
checks the key exists via `check_if_key_in_config`, deletes it from the
config dict, and calls `write_config`. Raises the same "unknown service"
error as `get_code`/`get_qrcode` when the service doesn't exist.

### `get_qrcode`

Rather than writing a `<service>.png` file to an arbitrary path on disk (as
the CLI's `-qr`/`--qrcode` flag does), this returns the QR image directly as
MCP image content so the host/agent can display it inline. It reuses
`qrcode.make(...)` from `share.generate_qrcode`, returning the encoded bytes
instead of saving to a file.

## Data flow

MCP host → stdio JSON-RPC → `mcp_server.py` tool function → `share.py`
function → reads/writes `~/.pyauthenticator` → result flows back the same
path.

## Error handling

- Today, `check_if_key_in_config` raises a bare `ValueError()` with no
  message, and `__main__.py` reconstructs a "did you mean one of: ..."
  message ad hoc for the CLI. This message-building is factored into a new
  `share.py` helper, `format_unknown_service_error(key, config_dict) ->
  str`, used by both the CLI and the MCP tools so the two surfaces produce
  the same helpful text instead of duplicating the logic.
- FastMCP automatically converts an exception raised inside a tool function
  into a tool-call error result (`isError: true` plus the exception
  message). Tools simply raise `ValueError(format_unknown_service_error(...))`
  and rely on the SDK for protocol translation — no custom error-handling
  scaffolding is needed.
- No new failure modes beyond what the CLI already surfaces today (bad QR
  image, unreadable file, malformed otpauth string): these continue to
  propagate as exceptions → MCP tool errors.

## Packaging, CI, docs

- `pyproject.toml`: add `[project.optional-dependencies]` with
  `mcp = ["mcp>=1.2.0"]`, and a new entry under `[project.scripts]`:
  `pyauthenticator-mcp = "pyauthenticator.mcp_server:main"`. CLI-only
  installs (`pip install pyauthenticator`) get no new dependency;
  `pip install pyauthenticator[mcp]` pulls in the SDK.
- CI (`.github/workflows/pipeline.yml`): the `unittest`, `coverage`, and
  `mypy` jobs need the `mcp` extra installed to exercise/type-check the new
  module. Add `mcp` to `.ci_support/environment.yml` and
  `.binder/environment.yml` (these jobs install dependencies via conda, then
  `pip install --no-deps .`).
- README: new "MCP Server" section under "For Developers" showing the
  `pyauthenticator[mcp]` install and an example Claude Desktop/Claude Code
  MCP config snippet:
  ```json
  {"mcpServers": {"pyauthenticator": {"command": "pyauthenticator-mcp"}}}
  ```

### Known risk

If the `mcp` package isn't available on conda-forge (or not at a compatible
version) at implementation time, the conda install path for this extra may
not resolve cleanly. The pip path (`pip install pyauthenticator[mcp]`) is
unaffected. Adding `mcp` to conda-forge (if it isn't already there) is
outside the scope of this repository and is called out here rather than
solved as part of this work.

## Testing

- `share.py` additions (`remove_service`, `format_unknown_service_error`,
  the `Image`-accepting refactor of `add_service`) get unit tests in
  `tests/test_share.py` alongside the existing ones, following the same
  style — no mocking of the filesystem beyond what the existing tests
  already do.
- `mcp_server.py`: the FastMCP-decorated functions remain plain callables,
  so tests call them directly against a temp config file (same pattern used
  by `tests/test_core.py`/`tests/test_cmd.py`) rather than spinning up a
  real stdio subprocess. One smoke test constructs the `FastMCP` instance
  and confirms all five tools are registered, to catch wiring mistakes
  (a typo in a decorator, a missing registration, etc.).
- No new test infrastructure is introduced — this continues to use
  `unittest` + `coverage`, matching the existing suite.
