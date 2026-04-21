"""
Simple stdio MCP client for the local Salesforce MCP server.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional


class MCPClient:
    def __init__(self, server_script: Optional[str] = None):
        base_dir = Path(__file__).resolve().parent
        self.server_script = server_script or str(base_dir / "mcp_server.py")
        venv_python = base_dir / "venv" / "bin" / "python"
        self.python_executable = str(venv_python) if venv_python.exists() else sys.executable
        self.process: Optional[subprocess.Popen[bytes]] = None
        self._request_id = 0

    def __enter__(self) -> "MCPClient":
        self.start()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def start(self) -> None:
        if self.process is not None:
            return
        self.process = subprocess.Popen(
            [self.python_executable, self.server_script],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def close(self) -> None:
        if self.process is None:
            return
        try:
            self.process.terminate()
            self.process.wait(timeout=2)
        except Exception:
            self.process.kill()
        self.process = None

    def initialize(self) -> Dict[str, Any]:
        result = self.request(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "salesforce-streamlit-client", "version": "1.0.0"},
            },
        )
        self.notify("notifications/initialized", {})
        return result

    def list_tools(self) -> Dict[str, Any]:
        return self.request("tools/list", {})

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        return self.request("tools/call", {"name": tool_name, "arguments": arguments})

    def notify(self, method: str, params: Dict[str, Any]) -> None:
        self._ensure_started()
        message = {"jsonrpc": "2.0", "method": method, "params": params}
        self._write_message(message)

    def request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        self._ensure_started()
        self._request_id += 1
        message = {"jsonrpc": "2.0", "id": self._request_id, "method": method, "params": params}
        self._write_message(message)
        response = self._read_message()
        if response.get("error"):
            raise RuntimeError(response["error"]["message"])
        return response.get("result", {})

    def _ensure_started(self) -> None:
        if self.process is None:
            self.start()

    def _write_message(self, message: Dict[str, Any]) -> None:
        if not self.process or not self.process.stdin:
            raise RuntimeError("MCP server process is not running")
        body = json.dumps(message).encode("utf-8")
        header = f"Content-Length: {len(body)}\r\n\r\n".encode("utf-8")
        self.process.stdin.write(header)
        self.process.stdin.write(body)
        self.process.stdin.flush()

    def _read_message(self) -> Dict[str, Any]:
        if not self.process or not self.process.stdout:
            raise RuntimeError("MCP server process is not running")

        headers: Dict[str, str] = {}
        while True:
            line = self.process.stdout.readline()
            if not line:
                error_message = "MCP server closed unexpectedly"
                if self.process.stderr:
                    stderr_output = self.process.stderr.read().decode("utf-8").strip()
                    if stderr_output:
                        error_message = stderr_output
                raise RuntimeError(error_message)
            if line in (b"\r\n", b"\n"):
                break
            header = line.decode("utf-8").strip()
            if ":" in header:
                key, value = header.split(":", 1)
                headers[key.strip().lower()] = value.strip()

        content_length = int(headers.get("content-length", "0"))
        payload = self.process.stdout.read(content_length)
        return json.loads(payload.decode("utf-8"))
