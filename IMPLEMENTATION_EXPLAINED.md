# Salesforce Agent Implementation Explained

This file explains how the current app works and how MCP is being used in the repo now.

## What changed

The project no longer uses the old in-process `mcp_protocol.py` dispatcher.

It now has:
- a real stdio MCP server in `mcp_server.py`
- a matching stdio client in `mcp_client.py`
- the Streamlit chat app calling tools through that server

That means tool execution now goes through an actual server/client boundary instead of a direct Python method call.

## Main flow

### 1. `app.py`

This is just the Streamlit entrypoint:

```python
from chat_app import main

if __name__ == "__main__":
    main()
```

### 2. `chat_app.py`

This is the user-facing chat interface.

It:
- shows the chat conversation
- shows the session ID
- stores conversation history
- sends the latest prompt to the agent
- shows tool details in the UI

The app uses `st.chat_input(...)` and `st.chat_message(...)`, so the UI behaves like a real user/agent chat.

### 3. `session_manager.py`

This keeps track of session IDs and conversation history.

That history is used to support follow-up questions in the same chat session.

### 4. `agent.py`

This is the orchestration layer.

It:
- collects the current chat context
- asks `llm.py` what action to take
- opens an MCP client connection
- initializes the MCP session
- calls `tools/list` or `tools/call` through the MCP server
- formats results into a readable assistant reply

### 5. `llm.py`

This decides what the agent should do.

It sends the model:
- the current session ID
- recent conversation history
- the latest user request
- the available tool schema

If Gemini fails, there is a fallback parser so the app can still route basic requests.

### 6. `mcp_client.py`

This is a real stdio MCP client.

It:
- starts `mcp_server.py` as a subprocess
- sends JSON-RPC messages with `Content-Length` framing
- reads framed JSON-RPC responses

Supported calls:
- `initialize`
- `tools/list`
- `tools/call`

### 7. `mcp_server.py`

This is the MCP server.

It:
- reads framed JSON-RPC messages from stdin
- dispatches supported MCP methods
- returns MCP-style responses on stdout

Currently implemented methods:
- `initialize`
- `notifications/initialized`
- `ping`
- `tools/list`
- `tools/call`

### 8. `tools.py`

This contains the real Salesforce tool functions:
- `get_record_tool`
- `update_record_tool`
- `summarize_record_tool`
- `validate_update_tool`

These functions talk to Salesforce using `simple-salesforce`.

## End-to-end message flow

When a user asks something in the chat:

1. `chat_app.py` receives the prompt.
2. The current session history is pulled from `session_manager.py`.
3. `agent.py` calls `decide_action(...)` in `llm.py`.
4. If a tool is needed, `agent.py` opens `MCPClient()`.
5. `mcp_client.py` starts `mcp_server.py`.
6. The client sends `initialize`.
7. The client sends `tools/call` or `tools/list`.
8. `mcp_server.py` routes the request to `tools.py`.
9. The Salesforce tool runs.
10. The result comes back through the MCP server to the client.
11. `agent.py` formats the response.
12. `chat_app.py` stores and renders the assistant reply.

## Is this standard MCP now?

This is much closer to a proper MCP implementation than before.

Why:
- it uses a real client/server split
- it uses stdio transport
- it uses JSON-RPC style requests and responses
- it uses `Content-Length` framing
- it exposes tools via `tools/list` and `tools/call`

## What is still minimal

This is still a focused MCP server, not a large feature-complete one.

What is not implemented yet:
- prompts support
- resources support
- broader MCP capabilities beyond tools
- external host packaging/instructions
- tests for the MCP framing and protocol behavior

## Short summary

The architecture is now:

1. Streamlit chat UI
2. Agent orchestration
3. MCP client
4. MCP server
5. Salesforce tools

So the repo now uses a real stdio MCP server for tool execution, while the chat session and follow-up question logic remain managed by the Streamlit app itself.
