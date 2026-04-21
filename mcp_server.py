"""
Minimal stdio MCP server for Salesforce tools.
"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, Optional

from tools import TOOLS


PROTOCOL_VERSION = "2024-11-05"

TOOL_DEFINITIONS: Dict[str, Dict[str, Any]] = {
    "get_record": {
        "description": "Retrieve a Salesforce record by ID",
        "inputSchema": {
            "type": "object",
            "properties": {
                "object_type": {"type": "string"},
                "record_id": {"type": "string"},
                "fields": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["object_type", "record_id"],
        },
    },
    "update_record": {
        "description": "Update a Salesforce record with new field values",
        "inputSchema": {
            "type": "object",
            "properties": {
                "object_type": {"type": "string"},
                "record_id": {"type": "string"},
                "fields": {"type": "object"},
            },
            "required": ["object_type", "record_id", "fields"],
        },
    },
    "summarize_record": {
        "description": "Summarize key information for a Salesforce record",
        "inputSchema": {
            "type": "object",
            "properties": {
                "object_type": {"type": "string"},
                "record_id": {"type": "string"},
            },
            "required": ["object_type", "record_id"],
        },
    },
    "validate_update": {
        "description": "Validate a proposed record update before execution",
        "inputSchema": {
            "type": "object",
            "properties": {
                "object_type": {"type": "string"},
                "record_id": {"type": "string"},
                "fields": {"type": "object"},
            },
            "required": ["object_type", "record_id", "fields"],
        },
    },
}


def _read_message() -> Optional[Dict[str, Any]]:
    headers: Dict[str, str] = {}
    while True:
        line = sys.stdin.buffer.readline()
        if not line:
            return None
        if line in (b"\r\n", b"\n"):
            break
        header = line.decode("utf-8").strip()
        if ":" in header:
            key, value = header.split(":", 1)
            headers[key.strip().lower()] = value.strip()

    content_length = int(headers.get("content-length", "0"))
    if content_length <= 0:
        return None

    payload = sys.stdin.buffer.read(content_length)
    if not payload:
        return None
    return json.loads(payload.decode("utf-8"))


def _write_message(message: Dict[str, Any]) -> None:
    body = json.dumps(message).encode("utf-8")
    header = f"Content-Length: {len(body)}\r\n\r\n".encode("utf-8")
    sys.stdout.buffer.write(header)
    sys.stdout.buffer.write(body)
    sys.stdout.buffer.flush()


def _success(message_id: Any, result: Dict[str, Any]) -> Dict[str, Any]:
    return {"jsonrpc": "2.0", "id": message_id, "result": result}


def _error(message_id: Any, code: int, message: str) -> Dict[str, Any]:
    return {"jsonrpc": "2.0", "id": message_id, "error": {"code": code, "message": message}}


def _handle_initialize(message_id: Any) -> Dict[str, Any]:
    return _success(
        message_id,
        {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {"name": "salesforce-mcp-agent", "version": "1.0.0"},
        },
    )


def _handle_tools_list(message_id: Any) -> Dict[str, Any]:
    tools = []
    for name, definition in TOOL_DEFINITIONS.items():
        tools.append(
            {
                "name": name,
                "description": definition["description"],
                "inputSchema": definition["inputSchema"],
            }
        )
    return _success(message_id, {"tools": tools})


def _handle_tools_call(message_id: Any, params: Dict[str, Any]) -> Dict[str, Any]:
    tool_name = params.get("name")
    arguments = params.get("arguments", {})

    if tool_name not in TOOLS:
        return _error(message_id, -32602, f"Unknown tool: {tool_name}")

    try:
        result = TOOLS[tool_name](**arguments)
        is_error = bool(result.get("error")) or result.get("status") == "error"
        return _success(
            message_id,
            {
                "content": [{"type": "text", "text": json.dumps(result, indent=2)}],
                "structuredContent": result,
                "isError": is_error,
            },
        )
    except Exception as exc:
        return _success(
            message_id,
            {
                "content": [{"type": "text", "text": str(exc)}],
                "structuredContent": {"error": str(exc)},
                "isError": True,
            },
        )


def _dispatch(message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    method = message.get("method")
    message_id = message.get("id")
    params = message.get("params", {})

    if method == "notifications/initialized":
        return None
    if method == "ping":
        return _success(message_id, {})
    if method == "initialize":
        return _handle_initialize(message_id)
    if method == "tools/list":
        return _handle_tools_list(message_id)
    if method == "tools/call":
        return _handle_tools_call(message_id, params)
    return _error(message_id, -32601, f"Method not found: {method}")


def main() -> None:
    while True:
        message = _read_message()
        if message is None:
            break
        response = _dispatch(message)
        if response is not None:
            _write_message(response)


if __name__ == "__main__":
    main()
