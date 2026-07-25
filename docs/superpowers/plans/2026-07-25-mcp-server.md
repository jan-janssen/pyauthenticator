# MCP Server for pyauthenticator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an MCP server to `pyauthenticator` so MCP-compatible hosts (Claude Desktop, Claude Code, etc.) can call `get_code`, `list_services`, `add_service`, `remove_service`, and `get_qrcode` as tools, instead of an agent shelling out to the CLI or importing the library directly.

**Architecture:** A new thin adapter module, `pyauthenticator/mcp_server.py`, built on the official `mcp` SDK's `FastMCP`. All actual logic (config load/write, TOTP generation, QR encode/decode) stays in `pyauthenticator/share.py`; the MCP module only registers tool functions that delegate to it. The `mcp` SDK is an optional dependency (`pip install pyauthenticator[mcp]`), and the server runs over stdio only.

**Tech Stack:** Python, `mcp` SDK (`mcp.server.fastmcp.FastMCP`), existing `pyotp`/`qrcode`/`pyzbar`/`Pillow` stack, `unittest` + `coverage` (matching the existing test suite).

## Global Constraints

- Full CLI parity: the server exposes add / remove / list / get, not a read-only subset (per spec §"Scope decisions").
- No audit logging or human-in-the-loop gating in this version — tools are transparent wrappers around existing `share.py` calls.
- stdio transport only — no network-reachable mode.
- The `mcp` SDK is an **optional** dependency (`[project.optional-dependencies] mcp`), never added to the package's core `dependencies`.
- `add_service` accepts exactly one of `qrcode_path` (existing file-based flow) or `qrcode_base64` (raw PNG bytes, base64-encoded, for agents that have the QR image in memory rather than on disk).
- Errors surface as plain exceptions with the same "unknown service" message the CLI already produces (via a shared `share.py` helper), not custom MCP error scaffolding.
- Testing continues to use `unittest` + `coverage`; no new test framework.

**Deviation from the spec's literal CI wording, discovered during planning:** the spec said to "add `mcp` to `.ci_support/environment.yml`". That file is shared, unmodified, by the existing `unittest` job's Python 3.9–3.13 matrix. The `mcp` package on conda-forge requires Python ≥3.10 (confirmed via `importlib.metadata.metadata('mcp')['Requires-Python']` locally, which reports `>=3.10`), so adding it there would break conda dependency resolution on the 3.9 leg and take down the entire existing test matrix. Task 5 instead adds a **new**, separate environment file and CI job fixed at Python 3.13 (matching the pattern already used by the existing `coverage`/`mypy` jobs, which are not matrixed), and the new test file skips itself when `mcp` isn't importable so the untouched 3.9–3.13 matrix keeps passing regardless.

---

### Task 1: Shared "unknown service" error message

**Files:**
- Modify: `pyauthenticator/share.py`
- Modify: `pyauthenticator/__main__.py:63-80`
- Test: `tests/test_share.py`

**Interfaces:**
- Produces: `format_unknown_service_error(key: str, config_dict: Dict[str, Any]) -> str` — used by Task 4's MCP tools and by the CLI.

- [ ] **Step 1: Write the failing test**

Add to `tests/test_share.py` (add `format_unknown_service_error` to the existing import block at the top):

```python
from pyauthenticator.share import (
    check_if_key_in_config,
    expand_path,
    format_unknown_service_error,
    get_otpauth_dict,
    load_config,
    write_config
)
```

Add this test method to `ShareTest`:

```python
    def test_format_unknown_service_error(self):
        message = format_unknown_service_error(
            key="test3",
            config_dict={"test": "value"}
        )
        lines = message.split("\n")
        self.assertEqual(lines[0], 'The service "test3" does not exist.')
        self.assertIn("  * test", lines)
        self.assertIn(
            "  pyauthenticator --add <qr-code.png> <servicename>", lines
        )
        empty_message = format_unknown_service_error(key="test3", config_dict={})
        self.assertEqual(
            empty_message.split("\n")[0],
            "The config file ~/.pyauthenticator does not contain any services. "
            "To add a new service use:"
        )
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests.test_share -v`
Expected: FAIL with `ImportError: cannot import name 'format_unknown_service_error'`

- [ ] **Step 3: Add the helper to `share.py`**

Add this function to `pyauthenticator/share.py`, directly after `check_if_key_in_config` (after line 91):

```python
def format_unknown_service_error(key: str, config_dict: Dict[str, Any]) -> str:
    """
    Build the human readable error message for a service which is not in the configuration

    Args:
        key (str): lower case name of the service which was not found
        config_dict (dict): configuration dictionary

    Returns:
        str: multi-line message listing configured services (if any) and how to add a new one
    """
    if len(config_dict) > 0:
        message_lines = [
            'The service "' + key + '" does not exist.',
            "",
            "The config file ~/.pyauthenticator contains the following services:",
        ]
        for service in list_services(config_dict=config_dict):
            message_lines.append("  * " + service)
        message_lines += [
            "",
            "Choose one of these or add a new service using:",
        ]
    else:
        message_lines = [
            "The config file ~/.pyauthenticator does not contain any services. To add a new service use:"
        ]
    message_lines += [
        "  pyauthenticator --add <qr-code.png> <servicename>",
        "",
    ]
    return "\n".join(message_lines)
```

`format_unknown_service_error` calls `list_services`, which is defined later in the file (line 165) — this is fine at call time since Python resolves the name when the function runs, not when it's defined.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest tests.test_share -v`
Expected: PASS

- [ ] **Step 5: Refactor `__main__.py` to use the helper**

In `pyauthenticator/__main__.py`, update the import block:

```python
from pyauthenticator.share import (
    add_service,
    format_unknown_service_error,
    generate_qrcode,
    get_two_factor_code,
    list_services,
    load_config,
)
```

Replace lines 63-80 (the `try/except ValueError` block inside `command_line_parser`):

```python
        try:
            print(get_two_factor_code(key=args.service, config_dict=config_dict))
        except ValueError:
            print(
                format_unknown_service_error(key=args.service, config_dict=config_dict)
            )
```

Note: `list_services` is no longer called directly in this block (it's used inside `format_unknown_service_error` now), but it stays imported and used elsewhere in the same file (line 30, building the argparse help text) — do not remove the import.

- [ ] **Step 6: Run the full existing suite to confirm no regression**

Run: `python -m unittest discover tests -v`
Expected: PASS — in particular `tests/test_cmd.py::CmdParserTest::test_main_generate_two_factor` must still pass unchanged, since it only checks the first line of the printed message (`'The service "test3" does not exist.'`), which the refactor preserves byte-for-byte.

- [ ] **Step 7: Commit**

```bash
git add pyauthenticator/share.py pyauthenticator/__main__.py tests/test_share.py
git commit -m "Extract shared unknown-service error message into share.py"
```

---

### Task 2: `remove_service`

**Files:**
- Modify: `pyauthenticator/share.py`
- Test: `tests/test_core.py`

**Interfaces:**
- Consumes: `check_if_key_in_config(key, config_dict)`, `write_config(config_dict, config_file_to_write)` (both already in `share.py`).
- Produces: `remove_service(key: str, config_dict: Dict[str, Any], config_file_to_write: str = config_file) -> None` — used by Task 4's `remove_service` MCP tool.

- [ ] **Step 1: Write the failing test**

Add `remove_service` and `write_config` to the import block at the top of `tests/test_core.py`:

```python
from pyauthenticator.share import (
    add_service,
    generate_qrcode,
    get_two_factor_code,
    list_services,
    load_config,
    remove_service,
    write_config
)
```

Add this test method to `TestCore`:

```python
    def test_remove_service(self):
        config_file_name = "test_remove_config.json"
        config_dict = {"test": self.config_dict["test"]}
        write_config(config_dict=config_dict, config_file_to_write=config_file_name)
        remove_service(
            key="test", config_dict=config_dict, config_file_to_write=config_file_name
        )
        config_reload = load_config(config_file_to_load=config_file_name)
        self.assertDictEqual(config_reload, {})
        with self.assertRaises(ValueError):
            remove_service(
                key="test", config_dict={}, config_file_to_write=config_file_name
            )
        os.remove(config_file_name)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests.test_core -v`
Expected: FAIL with `ImportError: cannot import name 'remove_service'`

- [ ] **Step 3: Implement `remove_service` in `share.py`**

Add this function directly after `add_service` (after line 145):

```python
def remove_service(
    key: str, config_dict: Dict[str, Any], config_file_to_write: str = config_file
) -> None:
    """
    Remove a service from the configuration file

    Args:
        key (str): lower case name of the service
        config_dict (dict): configuration dictionary
        config_file_to_write (str): path to config file
    """
    check_if_key_in_config(key=key, config_dict=config_dict)
    del config_dict[key]
    write_config(config_dict=config_dict, config_file_to_write=config_file_to_write)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest tests.test_core -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add pyauthenticator/share.py tests/test_core.py
git commit -m "Add remove_service to share.py"
```

---

### Task 3: Bytes-based QR support (`add_service_from_bytes`, `generate_qrcode_bytes`)

**Files:**
- Modify: `pyauthenticator/share.py`
- Test: `tests/test_core.py`

**Interfaces:**
- Consumes: `write_config`, `check_if_key_in_config`, `decode` (from `pyzbar.pyzbar`), `Image` (from `PIL`), `qrcode.make`.
- Produces:
  - `add_service_from_bytes(key: str, qrcode_png_bytes: bytes, config_dict: Dict[str, Any], config_file_to_write: str = config_file) -> None` — used by Task 4's `add_service` MCP tool.
  - `generate_qrcode_bytes(key: str, config_dict: Dict[str, Any]) -> bytes` — used by Task 4's `get_qrcode` MCP tool.
- `add_service`'s existing signature and behavior (file-path based) is unchanged from the outside; internally it now delegates to a shared helper.

- [ ] **Step 1: Write the failing tests**

Add `add_service_from_bytes` and `generate_qrcode_bytes` to the import block at the top of `tests/test_core.py` (now reads):

```python
from pyauthenticator.share import (
    add_service,
    add_service_from_bytes,
    generate_qrcode,
    generate_qrcode_bytes,
    get_two_factor_code,
    list_services,
    load_config,
    remove_service,
    write_config
)
```

Add these test methods to `TestCore`:

```python
    def test_add_service_from_bytes(self):
        config_file_name = "test_config_bytes.json"
        with open(self.qr_code_png, "rb") as f:
            qrcode_bytes = f.read()
        add_service_from_bytes(
            key="test",
            qrcode_png_bytes=qrcode_bytes,
            config_dict={},
            config_file_to_write=config_file_name,
        )
        config_reload = load_config(config_file_to_load=config_file_name)
        self.assertEqual(config_reload["test"], self.config_dict["test"])
        os.remove(config_file_name)

    def test_generate_qrcode_bytes(self):
        qrcode_bytes = generate_qrcode_bytes(key="test", config_dict=self.config_dict)
        add_service_from_bytes(
            key="test_roundtrip",
            qrcode_png_bytes=qrcode_bytes,
            config_dict={},
            config_file_to_write="test_roundtrip.json",
        )
        config_reload = load_config(config_file_to_load="test_roundtrip.json")
        self.assertEqual(config_reload["test_roundtrip"], self.config_dict["test"])
        os.remove("test_roundtrip.json")
```

(The second test round-trips `generate_qrcode_bytes` through `add_service_from_bytes` rather than pulling in `pyzbar`/`PIL` directly in the test file — it reuses machinery already under test, matching this file's existing style of testing through the public `share.py` functions.)

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m unittest tests.test_core -v`
Expected: FAIL with `ImportError: cannot import name 'add_service_from_bytes'`

- [ ] **Step 3: Implement in `share.py`**

Add `import io` to the top of `pyauthenticator/share.py` (alongside the existing `import json` / `import os`):

```python
import io
import json
import os
```

Replace the existing `add_service` function (lines 128-145) with:

```python
def _add_service_from_image(
    key: str,
    image: Image.Image,
    config_dict: Dict[str, Any],
    config_file_to_write: str = config_file,
) -> None:
    """
    Decode an otpauth QR code from an already opened image and add it to the configuration file

    Args:
        key (str): lower case name of the service
        image (PIL.Image.Image): decoded QR code image
        config_dict (dict): configuration dictionary
        config_file_to_write (str): path to config file
    """
    otpauth_str = decode(image)[0].data.decode("utf-8")
    config_dict[key] = otpauth_str
    write_config(config_dict=config_dict, config_file_to_write=config_file_to_write)


def add_service(
    key: str,
    qrcode_png_file_name: str,
    config_dict: Dict[str, Any],
    config_file_to_write: str = config_file,
) -> None:
    """
    Add new service to configuration file from a qrcode image file

    Args:
        key (str): lower case name of the service
        qrcode_png_file_name (str): path to the png file which contains the qr code
        config_dict (dict): configuration dictionary
        config_file_to_write (str): path to config file
    """
    _add_service_from_image(
        key=key,
        image=Image.open(qrcode_png_file_name),
        config_dict=config_dict,
        config_file_to_write=config_file_to_write,
    )


def add_service_from_bytes(
    key: str,
    qrcode_png_bytes: bytes,
    config_dict: Dict[str, Any],
    config_file_to_write: str = config_file,
) -> None:
    """
    Add new service to configuration file from the raw bytes of a qrcode png image

    Args:
        key (str): lower case name of the service
        qrcode_png_bytes (bytes): raw bytes of the png file which contains the qr code
        config_dict (dict): configuration dictionary
        config_file_to_write (str): path to config file
    """
    _add_service_from_image(
        key=key,
        image=Image.open(io.BytesIO(qrcode_png_bytes)),
        config_dict=config_dict,
        config_file_to_write=config_file_to_write,
    )
```

(`Image.Image` resolves directly here since `share.py` already imports `from PIL import Image` at the top of the file — no additional import needed.)

Add `generate_qrcode_bytes` directly after the existing `generate_qrcode` function (after line 162):

```python
def generate_qrcode_bytes(key: str, config_dict: Dict[str, Any]) -> bytes:
    """
    Generate the PNG bytes of a qrcode, without writing it to a file

    Args:
        key (str): lower case name of the service
        config_dict (dict): configuration dictionary

    Returns:
        bytes: PNG encoded qrcode image
    """
    check_if_key_in_config(key=key, config_dict=config_dict)
    buffer = io.BytesIO()
    qrcode.make(config_dict[key]).save(buffer, "PNG")
    return buffer.getvalue()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m unittest tests.test_core -v`
Expected: PASS

- [ ] **Step 5: Run the full existing suite to confirm no regression**

Run: `python -m unittest discover tests -v`
Expected: PASS — `test_add_service` in `tests/test_core.py` must still pass unchanged, since `add_service`'s external signature and behavior didn't change.

- [ ] **Step 6: Commit**

```bash
git add pyauthenticator/share.py tests/test_core.py
git commit -m "Add bytes-based QR decode/encode helpers to share.py"
```

---

### Task 4: MCP server module

**Files:**
- Create: `pyauthenticator/mcp_server.py`
- Create: `tests/test_mcp_server.py`

**Interfaces:**
- Consumes (all from `pyauthenticator.share`, added in Tasks 1-3 or pre-existing): `add_service`, `add_service_from_bytes`, `format_unknown_service_error`, `generate_qrcode_bytes`, `get_two_factor_code`, `list_services`, `load_config`, `remove_service`.
- Produces: module-level `mcp` (a `FastMCP` instance) and five tool functions — `get_code(service: str) -> str`, `list_services() -> List[str]`, `add_service(service: str, qrcode_path: Optional[str] = None, qrcode_base64: Optional[str] = None) -> str`, `remove_service(service: str) -> str`, `get_qrcode(service: str) -> Image` — plus `main() -> None`, the entry point used by Task 5's console script.

This task requires the `mcp` package to be installed locally to develop against (`pip install mcp==1.28.1`), but the resulting module is only imported by users who installed the `pyauthenticator[mcp]` extra — see Task 5.

- [ ] **Step 1: Install `mcp` locally for development**

Run: `pip install mcp==1.28.1`

- [ ] **Step 2: Write the failing test**

Create `tests/test_mcp_server.py`:

```python
"""
Test for the MCP server exposing pyauthenticator over the Model Context Protocol
"""
import asyncio
import base64
import os
import unittest

try:
    from pyauthenticator.mcp_server import (
        add_service,
        get_code,
        get_qrcode,
        list_services,
        mcp,
        remove_service,
    )
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

from pyauthenticator.share import config_file, expand_path, write_config


@unittest.skipUnless(MCP_AVAILABLE, "mcp package is not installed")
class TestMcpServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config_dict = {
            "test": "otpauth://totp/Test%3A%20root%40github.com?secret=6IQXETC4ADOSMMUN&issuer=Test"
        }
        cls.config_path = expand_path(config_file)
        if not os.path.exists(cls.config_path):
            write_config(config_dict=cls.config_dict)

    def test_tools_registered(self):
        tool_names = {tool.name for tool in asyncio.run(mcp.list_tools())}
        self.assertEqual(
            tool_names,
            {
                "get_code",
                "list_services",
                "add_service",
                "remove_service",
                "get_qrcode",
            },
        )

    def test_get_code(self):
        code = get_code(service="test")
        self.assertEqual(len(code), 6)

    def test_get_code_unknown_service(self):
        with self.assertRaises(ValueError) as context:
            get_code(service="does-not-exist")
        self.assertIn("does-not-exist", str(context.exception))

    def test_list_services(self):
        self.assertIn("test", list_services())

    def test_get_qrcode(self):
        image = get_qrcode(service="test")
        self.assertTrue(image.data)

    def test_add_and_remove_service(self):
        image = get_qrcode(service="test")
        qrcode_base64 = base64.b64encode(image.data).decode("utf-8")
        add_service(service="test_mcp_added", qrcode_base64=qrcode_base64)
        self.assertIn("test_mcp_added", list_services())
        remove_service(service="test_mcp_added")
        self.assertNotIn("test_mcp_added", list_services())

    def test_add_service_requires_exactly_one_source(self):
        with self.assertRaises(ValueError):
            add_service(service="test_mcp_invalid")
        with self.assertRaises(ValueError):
            add_service(
                service="test_mcp_invalid",
                qrcode_path="a.png",
                qrcode_base64="Yg==",
            )


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: Run test to verify it fails**

Run: `python -m unittest tests.test_mcp_server -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'pyauthenticator.mcp_server'`

- [ ] **Step 4: Implement `pyauthenticator/mcp_server.py`**

```python
"""
MCP server exposing pyauthenticator's two factor authentication functionality as MCP tools
"""
import base64
from typing import List, Optional

from mcp.server.fastmcp import FastMCP, Image

from pyauthenticator.share import add_service as _add_service
from pyauthenticator.share import add_service_from_bytes as _add_service_from_bytes
from pyauthenticator.share import format_unknown_service_error as _format_unknown_service_error
from pyauthenticator.share import generate_qrcode_bytes as _generate_qrcode_bytes
from pyauthenticator.share import get_two_factor_code as _get_two_factor_code
from pyauthenticator.share import list_services as _list_services
from pyauthenticator.share import load_config as _load_config
from pyauthenticator.share import remove_service as _remove_service

mcp = FastMCP(name="pyauthenticator")


@mcp.tool()
def get_code(service: str) -> str:
    """
    Generate the current two factor authentication code for a configured service.

    Args:
        service: lower case name of the service, as stored in ~/.pyauthenticator
    """
    config_dict = _load_config()
    try:
        return _get_two_factor_code(key=service, config_dict=config_dict)
    except ValueError:
        raise ValueError(
            _format_unknown_service_error(key=service, config_dict=config_dict)
        )


@mcp.tool()
def list_services() -> List[str]:
    """
    List the names of all services currently configured in ~/.pyauthenticator.
    """
    return _list_services(config_dict=_load_config())


@mcp.tool()
def add_service(
    service: str,
    qrcode_path: Optional[str] = None,
    qrcode_base64: Optional[str] = None,
) -> str:
    """
    Add a new service by decoding an otpauth QR code, either from a file path or from
    base64 encoded PNG bytes. Exactly one of qrcode_path or qrcode_base64 must be given.

    Args:
        service: lower case name to store the service under
        qrcode_path: path to a PNG file containing the QR code
        qrcode_base64: base64 encoded PNG bytes containing the QR code
    """
    if (qrcode_path is None) == (qrcode_base64 is None):
        raise ValueError("Provide exactly one of qrcode_path or qrcode_base64")
    config_dict = _load_config()
    if qrcode_path is not None:
        _add_service(
            key=service, qrcode_png_file_name=qrcode_path, config_dict=config_dict
        )
    else:
        _add_service_from_bytes(
            key=service,
            qrcode_png_bytes=base64.b64decode(qrcode_base64),
            config_dict=config_dict,
        )
    return "The service '" + service + "' was added."


@mcp.tool()
def remove_service(service: str) -> str:
    """
    Remove a service from ~/.pyauthenticator.

    Args:
        service: lower case name of the service to remove
    """
    config_dict = _load_config()
    try:
        _remove_service(key=service, config_dict=config_dict)
    except ValueError:
        raise ValueError(
            _format_unknown_service_error(key=service, config_dict=config_dict)
        )
    return "The service '" + service + "' was removed."


@mcp.tool()
def get_qrcode(service: str) -> Image:
    """
    Generate a QR code image for a configured service, to scan with a mobile authenticator app.

    Args:
        service: lower case name of the service
    """
    config_dict = _load_config()
    try:
        qrcode_bytes = _generate_qrcode_bytes(key=service, config_dict=config_dict)
    except ValueError:
        raise ValueError(
            _format_unknown_service_error(key=service, config_dict=config_dict)
        )
    return Image(data=qrcode_bytes, format="png")


def main() -> None:
    """
    Entry point for the `pyauthenticator-mcp` console script.
    """
    mcp.run()


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Run test to verify it passes**

Run: `python -m unittest tests.test_mcp_server -v`
Expected: PASS (7 tests)

- [ ] **Step 6: Run the full existing suite to confirm no regression**

Run: `python -m unittest discover tests -v`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add pyauthenticator/mcp_server.py tests/test_mcp_server.py
git commit -m "Add MCP server exposing get/list/add/remove/get_qrcode tools"
```

---

### Task 5: Packaging, CI, docs

**Files:**
- Modify: `pyproject.toml`
- Create: `.ci_support/environment-mcp.yml`
- Modify: `.binder/environment.yml`
- Modify: `.github/workflows/pipeline.yml`
- Modify: `README.md`

**Interfaces:**
- Consumes: `pyauthenticator.mcp_server:main` (from Task 4).
- Produces: `pyauthenticator-mcp` console script; `pip install pyauthenticator[mcp]` extra; a new `mcp_server_test` CI job.

- [ ] **Step 1: Add the optional dependency and console script to `pyproject.toml`**

Add this new table directly after the existing `dependencies = [...]` block (after line 44):

```toml
[project.optional-dependencies]
mcp = ["mcp==1.28.1"]
```

Update `[project.scripts]` (currently line 52-53) to:

```toml
[project.scripts]
pyauthenticator = "pyauthenticator.__main__:command_line_parser"
pyauthenticator-mcp = "pyauthenticator.mcp_server:main"
```

- [ ] **Step 2: Add a dedicated conda environment file for the MCP CI job**

Create `.ci_support/environment-mcp.yml`, copying `.ci_support/environment.yml` and adding `mcp`:

```yaml
channels:
- conda-forge
dependencies:
- python
- coverage
- hatchling =1.27.0
- hatch-vcs =0.5.0
- qrcode=8.2
- pyotp=2.9.0
- pyzbar=0.1.9
- zbar=0.10
- pillow=11.3.0
- mcp=1.28.1
```

This file is deliberately separate from `.ci_support/environment.yml` (used unchanged by the existing 3.9–3.13 `unittest` matrix) because `mcp` requires Python ≥3.10 and would otherwise break conda's dependency resolution on the 3.9 leg — see the "Deviation" note in Global Constraints above.

- [ ] **Step 3: Add `mcp` to the Binder environment for interactive use**

In `.binder/environment.yml`, add `mcp` to the dependency list:

```yaml
channels:
- conda-forge
dependencies:
- python
- qrcode
- pyotp
- pyzbar
- zbar
- pillow
- mcp
```

- [ ] **Step 4: Add a new CI job for the MCP server tests**

In `.github/workflows/pipeline.yml`, add this job (fixed at Python 3.13, following the same pattern as the existing `coverage` job, but using the new environment file and running only the MCP test module):

```yaml
  mcp_server_test:
    needs: [black]
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Conda config
      shell: bash -l {0}
      run: echo -e "channels:\n  - conda-forge\n" > .condarc
    - uses: conda-incubator/setup-miniconda@v3
      with:
        python-version: '3.13'
        miniforge-version: latest
        condarc-file: .condarc
        environment-file: .ci_support/environment-mcp.yml
    - name: Test
      shell: bash -l {0}
      run: |
        pip install --no-deps .
        python -m unittest tests.test_mcp_server -v
```

Insert it as a new top-level job (e.g. directly after the existing `mypy` job), keeping the existing `black`, `black_fix`, `mypy`, `pip_check`, `unittest`, and `coverage` jobs unchanged.

- [ ] **Step 5: Document the MCP server in the README**

In `README.md`, add this new section directly before `## License` (currently line 92). Copy the following block verbatim into the file (the outer ```` ```` ```` fence below is just this plan's container — do not include those four-backtick lines themselves in `README.md`):

`````markdown
## MCP Server
`pyauthenticator` also ships an [MCP](https://modelcontextprotocol.io) server, so AI agents and other
MCP-compatible hosts can request two factor authentication codes through a controlled tool interface instead of
importing the library directly or shelling out to the CLI. Install the optional `mcp` extra:
```
>>> pip install pyauthenticator[mcp]
```
Then point an MCP host at the `pyauthenticator-mcp` command, for example in a Claude Desktop or Claude Code MCP
configuration file:
```json
{
  "mcpServers": {
    "pyauthenticator": {
      "command": "pyauthenticator-mcp"
    }
  }
}
```
The server exposes five tools — `get_code`, `list_services`, `add_service`, `remove_service`, and `get_qrcode` —
mirroring the functionality available on the command line.
`````

- [ ] **Step 6: Verify locally**

Run: `python -m unittest discover tests -v`
Expected: PASS (all tests, including `tests/test_mcp_server.py`, since `mcp` was installed locally in Task 4 Step 1)

Run: `pip install -e .`
Expected: succeeds; `pyauthenticator-mcp` becomes available on `PATH` (check with `which pyauthenticator-mcp`)

- [ ] **Step 7: Commit**

```bash
git add pyproject.toml .ci_support/environment-mcp.yml .binder/environment.yml .github/workflows/pipeline.yml README.md
git commit -m "Package the MCP server as an optional extra, with CI and docs"
```
