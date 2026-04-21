# llm.py

import google.generativeai as genai
import os
import json
import re
from typing import Any, Dict, Optional
from dotenv import load_dotenv
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import Annotated, TypedDict

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")


class AgentState(TypedDict):
    """State definition for LangGraph workflow"""
    messages: Annotated[list, add_messages]
    tool_calls: list
    tool_results: list
    final_response: str
    current_action: Optional[str]


# Enhanced tools schema for MCP-style local tool routing
TOOLS_SCHEMA = """
You are a Salesforce MCP (Model Context Protocol) agent with access to the following tools:

Available Tools:

1. get_record
   - Description: Retrieve a Salesforce record by ID
   - Parameters: object_type (str), record_id (str), fields (list, optional)
   - Returns: Record data or error

2. update_record
   - Description: Update a Salesforce record with new field values
   - Parameters: object_type (str), record_id (str), fields (dict)
   - Returns: Status confirmation or error

3. summarize_record
   - Description: Retrieve and summarize a record's key information
   - Parameters: object_type (str), record_id (str)
   - Returns: Summarized record data

4. validate_update
   - Description: Validate a proposed update before applying it
   - Parameters: object_type (str), record_id (str), fields (dict)
   - Returns: Validation result with warnings

Decision Rules:
- Always assess if the user request requires a tool call
- If information is missing, DO NOT call tool - ask for clarification
- Call validate_update BEFORE update_record for safety
- Return structured JSON responses

Response Formats:

1. For tool call:
{
  "type": "tool_call",
  "tool": "tool_name",
  "parameters": {
    "parameter": "value"
  }
}

2. For clarification:
{
  "type": "clarification",
  "message": "What information do you need?"
}

3. For final response:
{
  "type": "response",
  "message": "Your response here"
}
"""


def clean_json(text: str) -> str:
    """Clean JSON response from model output"""
    return text.replace("```json", "").replace("```", "").strip()


def _extract_object_type(text: str) -> Optional[str]:
    match = re.search(r"\b(Account|Contact|Opportunity|Lead|Case)\b", text, re.IGNORECASE)
    return match.group(1).title() if match else None


def _extract_record_id(text: str) -> Optional[str]:
    match = re.search(r"\b([A-Za-z0-9]{15,18})\b", text)
    return match.group(1) if match else None


def _extract_update_fields(text: str) -> Dict[str, Any]:
    fields: Dict[str, Any] = {}

    patterns = [
        r'field\s+"?([A-Za-z0-9_]+)"?\s+to\s+(.+)',
        r'change\s+"?([A-Za-z0-9_]+)"?\s+to\s+(.+)',
        r'update\s+"?([A-Za-z0-9_]+)"?\s+to\s+(.+)',
        r'set\s+"?([A-Za-z0-9_]+)"?\s+to\s+(.+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            field_name = match.group(1).strip()
            field_value = match.group(2).strip().strip(",").strip()
            if field_name and field_value:
                fields[field_name] = field_value
                return fields

    return fields


def _fallback_decision(user_input: str) -> Dict[str, Any]:
    lowered = user_input.lower()
    object_type = _extract_object_type(user_input)
    record_id = _extract_record_id(user_input)

    if "what tools" in lowered or "list tools" in lowered or "available tools" in lowered:
        return {
            "type": "response",
            "message": "Available tools: get_record, update_record, summarize_record, validate_update."
        }

    if "summarize" in lowered:
        if object_type and record_id:
            return {
                "type": "tool_call",
                "tool": "summarize_record",
                "parameters": {"object_type": object_type, "record_id": record_id},
            }
        return {
            "type": "clarification",
            "message": "Please share the Salesforce object type and record ID you want summarized.",
        }

    if "update" in lowered:
        if object_type and record_id:
            fields = _extract_update_fields(user_input)
            if fields:
                return {
                    "type": "tool_call",
                    "tool": "update_record",
                    "parameters": {"object_type": object_type, "record_id": record_id, "fields": fields},
                }
        return {
            "type": "clarification",
            "message": "Please share the object type, record ID, and field changes you want to update.",
        }

    if any(word in lowered for word in ["get", "show", "fetch"]):
        if object_type and record_id:
            return {
                "type": "tool_call",
                "tool": "get_record",
                "parameters": {"object_type": object_type, "record_id": record_id},
            }
        return {
            "type": "clarification",
            "message": "Please share the Salesforce object type and record ID you want to retrieve.",
        }

    return {
        "type": "clarification",
        "message": "Please rephrase your Salesforce request with an object type and record ID.",
    }


def decide_action(user_input: str, conversation_context: str = "", session_id: str = "") -> Dict[str, Any]:
    """
    Use LLM to decide what action to take based on user input.
    Returns structured decision with tool calls or clarification requests.
    """
    prompt = (
        TOOLS_SCHEMA
        + f"\n\nSession ID: {session_id or 'unknown'}"
        + f"\n\nConversation Context:\n{conversation_context or 'No prior context.'}"
        + f"\n\nLatest User Request: {user_input}"
    )

    try:
        response = model.generate_content(prompt)
        return json.loads(clean_json(response.text))
    except Exception:
        return _fallback_decision(user_input)


def route_handler(state: AgentState) -> str:
    """Route to next step based on current state"""
    if state.get("current_action") == "tool_call":
        return "execute_tool"
    elif state.get("current_action") == "clarification":
        return "clarify"
    else:
        return "respond"


def process_input_node(state: AgentState) -> Dict[str, Any]:
    """Process user input and decide action"""
    latest_message = state["messages"][-1]
    decision = decide_action(latest_message)
    
    return {
        "current_action": decision.get("type"),
        "tool_calls": [decision] if decision.get("type") == "tool_call" else [],
        "messages": state["messages"],
        "final_response": decision.get("message") if decision.get("type") != "tool_call" else ""
    }


def tool_executor_node(state: AgentState) -> Dict[str, Any]:
    """Execute tool calls"""
    from tools import TOOLS
    
    results = []
    for tool_call in state.get("tool_calls", []):
        tool_name = tool_call.get("tool")
        params = tool_call.get("parameters", {})
        
        if tool_name in TOOLS:
            try:
                result = TOOLS[tool_name](**params)
                results.append({
                    "tool": tool_name,
                    "status": "success",
                    "result": result
                })
            except Exception as e:
                results.append({
                    "tool": tool_name,
                    "status": "error",
                    "result": str(e)
                })
        else:
            results.append({
                "tool": tool_name,
                "status": "error",
                "result": f"Unknown tool: {tool_name}"
            })
    
    return {
        "tool_results": results,
        "current_action": "respond"
    }


def clarify_node(state: AgentState) -> Dict[str, Any]:
    """Handle clarification requests"""
    return {
        "final_response": state.get("messages", [])[-1] if state.get("messages") else "Please provide more details."
    }


def respond_node(state: AgentState) -> Dict[str, Any]:
    """Generate final response"""
    if state.get("tool_results"):
        # Format tool results for response
        results_summary = json.dumps(state["tool_results"], indent=2)
        response = f"Tool execution results:\n{results_summary}"
    else:
        response = state.get("final_response", "Request processed.")
    
    return {
        "final_response": response
    }


def create_workflow():
    """Create LangGraph workflow for local MCP-style routing"""
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("process_input", process_input_node)
    workflow.add_node("execute_tool", tool_executor_node)
    workflow.add_node("clarify", clarify_node)
    workflow.add_node("respond", respond_node)
    
    # Set entry point
    workflow.set_entry_point("process_input")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "process_input",
        lambda state: state.get("current_action", "respond"),
        {
            "tool_call": "execute_tool",
            "clarification": "clarify",
            "response": "respond"
        }
    )
    
    # Add edges to respond
    workflow.add_edge("execute_tool", "respond")
    workflow.add_edge("clarify", "respond")
    
    return workflow.compile()


# Create the workflow
mcp_workflow = create_workflow()
