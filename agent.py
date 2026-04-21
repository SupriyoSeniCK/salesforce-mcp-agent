from llm import decide_action
from mcp_client import MCPClient


def _format_tool_content(tool_name: str, content: dict) -> str:
    if content.get("error"):
        return f"{tool_name} failed: {content['error']}"

    if tool_name == "get_record":
        summary = content.get("summary", {})
        return (
            f"Retrieved {summary.get('type', 'record')} {summary.get('id', '')}.\n"
            f"Name: {summary.get('name', 'N/A')}\n"
            f"Created: {summary.get('created_date', 'N/A')}\n"
            f"Last Modified: {summary.get('last_modified', 'N/A')}"
        )

    if tool_name == "summarize_record":
        return (
            f"Summary for {content.get('type', 'record')} {content.get('id', '')}:\n"
            f"Name: {content.get('name', 'N/A')}\n"
            f"Created: {content.get('created_date', 'N/A')}\n"
            f"Last Modified: {content.get('last_modified', 'N/A')}"
        )

    if tool_name == "update_record":
        return content.get("message", "Record updated successfully.")

    if tool_name == "validate_update":
        warnings = content.get("warnings", [])
        warning_text = f"\nWarnings: {', '.join(warnings)}" if warnings else ""
        return f"Validation {'passed' if content.get('valid') else 'failed'} for {content.get('record_id', '')}.{warning_text}"

    return str(content)


def handle_query(user_input: str, conversation_context: str = "", session_id: str = "") -> dict:
    """Handle a user query through the MCP server."""
    try:
        with MCPClient() as client:
            init_result = client.initialize()
            resolved_session_id = session_id or f"chat-{init_result.get('serverInfo', {}).get('version', '1.0.0')}"
            decision = decide_action(user_input, conversation_context, resolved_session_id)

            if decision.get("type") == "tool_call":
                tool_name = decision.get("tool")
                params = decision.get("parameters", {})
                tool_result = client.call_tool(tool_name, params)
                content = tool_result.get("structuredContent", {})
                response_text = _format_tool_content(tool_name, content)
                return {
                    "response": response_text,
                    "session_id": resolved_session_id,
                    "decision": decision,
                    "tool_info": tool_result,
                }

            return {
                "response": decision.get("message", "No response generated"),
                "session_id": resolved_session_id,
                "decision": decision,
                "tool_info": None,
            }
    except Exception as exc:
        return {
            "response": f"Error processing query: {str(exc)}",
            "session_id": session_id,
            "decision": None,
            "tool_info": None,
        }


def handle_query_with_validation(user_input: str, conversation_context: str = "", session_id: str = "") -> dict:
    """Handle a user query and enforce validate-then-update for updates."""
    try:
        with MCPClient() as client:
            init_result = client.initialize()
            resolved_session_id = session_id or f"chat-{init_result.get('serverInfo', {}).get('version', '1.0.0')}"
            decision = decide_action(user_input, conversation_context, resolved_session_id)
            result = {
                "user_input": user_input,
                "session_id": resolved_session_id,
                "decision_type": decision.get("type"),
                "response": "",
            }

            if decision.get("type") == "tool_call":
                tool_name = decision.get("tool")
                params = decision.get("parameters", {})

                if tool_name == "update_record":
                    validation_response = client.call_tool(
                        "validate_update",
                        {
                            "object_type": params.get("object_type"),
                            "record_id": params.get("record_id"),
                            "fields": params.get("fields"),
                        },
                    )
                    validation = validation_response.get("structuredContent", {})
                    result["validation"] = validation

                    if validation.get("valid"):
                        update_response = client.call_tool("update_record", params)
                        update_result = update_response.get("structuredContent", {})
                        result["response"] = f"Update validated and applied: {_format_tool_content('update_record', update_result)}"
                        result["tool_info"] = update_response
                    else:
                        result["response"] = f"Update validation failed: {validation}"
                else:
                    tool_result = client.call_tool(tool_name, params)
                    content = tool_result.get("structuredContent", {})
                    result["response"] = _format_tool_content(tool_name, content)
                    result["tool_info"] = tool_result
            else:
                result["response"] = decision.get("message", "No response")

            return result
    except Exception as exc:
        return {
            "user_input": user_input,
            "session_id": session_id,
            "decision_type": "error",
            "response": f"Error processing query: {str(exc)}",
        }


def list_mcp_tools(session_id: str = "") -> dict:
    """List tools from the MCP server."""
    try:
        with MCPClient() as client:
            client.initialize()
            result = client.list_tools()
            return {"session_id": session_id, "result": result}
    except Exception as exc:
        return {"session_id": session_id, "error": str(exc)}
