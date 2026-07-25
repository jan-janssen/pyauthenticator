"""
MCP server for pyauthenticator.
"""

import base64
import io
from typing import Any, List, Optional

from PIL import Image as PilImage

from pyauthenticator.share import (
    add_service as add_service_from_path,
    add_service_from_image,
    format_unknown_service_error,
    get_qrcode_image,
    get_two_factor_code as get_two_factor_code_internal,
    list_services as list_services_internal,
    load_config,
    remove_service as remove_service_internal,
)

FastMCP = None
MCPImage = None
MCP_IMPORT_ERROR: Optional[ImportError] = None

try:
    from mcp.server.fastmcp import FastMCP as _FastMCP
    from mcp.server.fastmcp import Image as _MCPImage
except ImportError as import_error:
    MCP_IMPORT_ERROR = import_error
else:
    FastMCP = _FastMCP
    MCPImage = _MCPImage


def _require_mcp() -> Any:
    if FastMCP is None or MCPImage is None:
        raise ImportError(
            "The MCP server requires the optional 'mcp' dependency. "
            "Install it with 'pip install pyauthenticator[mcp]'."
        ) from MCP_IMPORT_ERROR
    return FastMCP, MCPImage


def get_code(service: str) -> str:
    """
    Generate a two factor authentication code for a configured service.
    """
    config_dict = load_config()
    try:
        return get_two_factor_code_internal(key=service, config_dict=config_dict)
    except ValueError as error:
        raise ValueError(
            format_unknown_service_error(key=service, config_dict=config_dict)
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
    except ValueError as error:
        raise ValueError(
            "qrcode_base64 must be valid base64-encoded PNG data"
        ) from error
    with PilImage.open(io.BytesIO(qrcode_bytes)) as qrcode_image:
        add_service_from_image(
            key=service, qrcode_image=qrcode_image, config_dict=config_dict
        )
    return "The service '" + service + "' was added from the provided QR code."


def remove_service(service: str) -> str:
    """
    Remove a configured service.
    """
    config_dict = load_config()
    try:
        remove_service_internal(key=service, config_dict=config_dict)
    except ValueError as error:
        raise ValueError(
            format_unknown_service_error(key=service, config_dict=config_dict)
        ) from error
    return "The service '" + service + "' was removed."


def get_qrcode(service: str) -> Any:
    """
    Return the QR code for a configured service as MCP image content.
    """
    _, image_class = _require_mcp()
    config_dict = load_config()
    try:
        qrcode_image = get_qrcode_image(key=service, config_dict=config_dict)
    except ValueError as error:
        raise ValueError(
            format_unknown_service_error(key=service, config_dict=config_dict)
        ) from error
    qrcode_buffer = io.BytesIO()
    qrcode_image.save(qrcode_buffer, "PNG")
    return image_class(data=qrcode_buffer.getvalue(), format="png")


def create_mcp_server() -> Any:
    """
    Create the FastMCP server instance.
    """
    fast_mcp_class, _ = _require_mcp()
    mcp = fast_mcp_class("pyauthenticator")
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


if FastMCP is not None and MCPImage is not None:
    mcp = create_mcp_server()
else:
    mcp = None


def main() -> None:
    """
    Run the MCP server using stdio transport.
    """
    create_mcp_server().run(transport="stdio")
