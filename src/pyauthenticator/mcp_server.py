"""
MCP server for pyauthenticator.
"""

import base64
import binascii
import io
from typing import Any, Dict, List, Optional

import qrcode
from PIL import Image as PilImage
from pyzbar.pyzbar import decode
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp import Image

from pyauthenticator._config import load_config, write_config
from pyauthenticator.api import (
    add_service as add_service_from_path,
)
from pyauthenticator.api import (
    get_totp_for_key_in_dict,
)
from pyauthenticator.api import (
    list_services as list_services_internal,
)


def _format_unknown_service_error(service: str, config_dict: Dict[str, Any]) -> str:
    if len(config_dict) > 0:
        return "\n".join(
            ['The service "' + service + '" does not exist.', ""]
            + ["The config file ~/.pyauthenticator contains the following services:"]
            + [
                "  * " + entry
                for entry in list_services_internal(config_dict=config_dict)
            ]
            + [
                "",
                "Choose one of these or add a new service using:",
                "  pyauthenticator --add <qr-code.png> <servicename>",
            ]
        )
    return "\n".join(
        [
            "The config file ~/.pyauthenticator does not contain any services. To add a new service use:",
            "  pyauthenticator --add <qr-code.png> <servicename>",
        ]
    )


def _add_service_from_image(service: str, qrcode_image: PilImage.Image) -> None:
    config_dict = load_config()
    config_dict[service] = decode(qrcode_image)[0].data.decode("utf-8")
    write_config(config_dict=config_dict)


def get_code(service: str) -> str:
    """
    Generate a two factor authentication code for a configured service.
    """
    config_dict = load_config()
    try:
        return get_totp_for_key_in_dict(key=service, config_dict=config_dict)
    except KeyError as error:
        raise ValueError(
            _format_unknown_service_error(service=service, config_dict=config_dict)
        ) from error


def list_services() -> List[str]:
    """
    List configured services.
    """
    return list_services_internal(config_dict=load_config())


def add_service(
    service: str, qrcode_path: Optional[str] = None, qrcode_base64: Optional[str] = None
) -> str:
    """
    Add a new service from a QR code path or base64 encoded PNG bytes.
    """
    if (qrcode_path is None) == (qrcode_base64 is None):
        raise ValueError("Provide exactly one of qrcode_path or qrcode_base64")
    config_dict = load_config()
    if qrcode_path is not None:
        add_service_from_path(
            key=service, qrcode_png_file_name=qrcode_path, config_dict=config_dict
        )
        return (
            "The service '" + service + "' was added, from file <" + qrcode_path + ">."
        )
    assert qrcode_base64 is not None
    try:
        qrcode_bytes = base64.b64decode(qrcode_base64.encode("utf-8"), validate=True)
    except (binascii.Error, ValueError) as error:
        raise ValueError(
            "qrcode_base64 must be valid base64-encoded PNG data"
        ) from error
    with PilImage.open(io.BytesIO(qrcode_bytes)) as qrcode_image:
        _add_service_from_image(service=service, qrcode_image=qrcode_image)
    return "The service '" + service + "' was added from the provided QR code."


def remove_service(service: str) -> str:
    """
    Remove a configured service.
    """
    config_dict = load_config()
    if service not in config_dict:
        raise ValueError(
            _format_unknown_service_error(service=service, config_dict=config_dict)
        )
    del config_dict[service]
    write_config(config_dict=config_dict)
    return "The service '" + service + "' was removed."


def get_qrcode(service: str) -> Any:
    """
    Return the QR code for a configured service as MCP image content.
    """
    config_dict = load_config()
    if service not in config_dict:
        raise ValueError(
            _format_unknown_service_error(service=service, config_dict=config_dict)
        )
    qrcode_buffer = io.BytesIO()
    qrcode.make(config_dict[service]).save(qrcode_buffer, "PNG")
    return Image(data=qrcode_buffer.getvalue(), format="png")


def create_mcp_server() -> Any:
    """
    Create the FastMCP server instance.
    """
    mcp = FastMCP("pyauthenticator")
    mcp.tool(
        name="get_code",
        description="Generate a two factor authentication code for a configured service.",
    )(get_code)
    mcp.tool(
        name="list_services",
        description="List the configured service names.",
    )(list_services)
    mcp.tool(
        name="add_service",
        description="Add a service from either qrcode_path or qrcode_base64. Provide exactly one of these arguments. qrcode_base64 must be a base64-encoded PNG image.",
    )(add_service)
    mcp.tool(
        name="remove_service",
        description="Remove a configured service.",
    )(remove_service)
    mcp.tool(
        name="get_qrcode",
        description="Return the configured service QR code as a PNG image.",
    )(get_qrcode)
    return mcp


mcp = create_mcp_server()


def main() -> None:
    """
    Run the MCP server using stdio transport.
    """
    create_mcp_server().run(transport="stdio")
