# MCP_IMPLEMENTATION.md
# Real MCP Implementation Guide

## Overview

This is a **production-grade Model Context Protocol (MCP) implementation** for Salesforce that enables intelligent tool orchestration with the following components:

### Architecture Components

```
┌──────────────────────────────────────────────────────────────┐
│                    HTTP Server                               │
│              (FastAPI - mcp_server_http.py)                  │
│  REST API for remote client access                           │
└──────────────────┬───────────────────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────────────────┐
│              Orchestration Agent                             │
│        (orchestrated_agent.py - LLM + MCP)                   │
│  Intelligent decision making and workflow routing            │
└──────────────────┬───────────────────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────────────────┐
│                 MCP Client                                   │
│           (mcp_client.py - Workflow Builder)                 │
│  Workflow orchestration and tool sequencing                  │
└──────────────────┬───────────────────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────────────────┐
│               MCP Server                                     │
│      (mcp_server.py - Protocol Handler)                      │
│  Tool definitions, schemas, and execution                    │
└──────────────────┬───────────────────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────────────────┐
│             Salesforce Tools                                 │
│              (tools.py - Implementations)                    │
│  get_record, update_record, summarize_record, validate_update
└──────────────────────────────────────────────────────────────┘
```

---

## File Structure

```
salesforce-mcp-agent/
├── mcp_server.py              # Core MCP protocol & tool registry
├── mcp_client.py              # MCP client & workflow builder
├── orchestrated_agent.py       # LLM-based intelligent agent
├── mcp_server_http.py         # FastAPI HTTP server
├── tools.py                   # Salesforce tool implementations
├── llm.py                     # LLM configuration
├── agent.py                   # Legacy agent (compatibility)
├── app.py                     # Streamlit UI
├── requirements.txt           # Dependencies
└── MCP_IMPLEMENTATION.md      # This file
```

---

## Core Components

### 1. MCP Server (`mcp_server.py`)

**Handles:**
- Tool registration and definitions
- JSON schema generation
- MCP protocol request/response
- Tool execution with error handling

**Key Classes:**
```python
ToolDefinition         # Tool metadata
MCPToolRegistry        # Tool registry and executor
MCPRequest             # Protocol requests
MCPResponse            # Protocol responses
MCPOrchestrator        # Main orchestrator
```

**Protocol Methods:**
- `tools/list` - List all available tools
- `tools/describe` - Get tool schema
- `tools/call` - Execute a tool
- `initialize` - Initialize session
- `ping` - Health check

### 2. MCP Client (`mcp_client.py`)

**Provides:**
- Tool execution interface
- Workflow building
- Workflow sequencing
- Tool call orchestration

**Key Classes:**
```python
MCPClient              # Client for server communication
MCPWorkflowBuilder     # Build multi-step workflows
MCPOrchestrationEngine # High-level orchestration
```

**Usage:**
```python
client = MCPClient(orchestrator)
await client.initialize()

# Execute single tool
result = await client.call_tool("get_record", {"object_type": "Account", ...})

# Build and execute workflow
builder = MCPWorkflowBuilder(client)
builder.add_step("get", "get_record", {...})
builder.add_step("summarize", "summarize_record", {...})
result = await builder.execute()
```

### 3. Orchestrated Agent (`orchestrated_agent.py`)

**Features:**
- LLM-based intelligent decision making
- Automatic tool selection
- Workflow generation
- Execution history tracking

**Modes:**
- `INTELLIGENT` - LLM decides tool/workflow
- `SINGLE_TOOL` - Execute single tool
- `WORKFLOW` - Execute pre-defined workflow
- `VALIDATION` - With safety validation

**Usage:**
```python
agent = OrchestrationAgent(mode=AgentMode.INTELLIGENT)
await agent.initialize()

# Process user query
result = await agent.process_query("Get the Account 001Xx000010SQA")

# Specific workflows
result = await agent.validate_and_update("Account", record_id, fields)
result = await agent.enrich_record("Account", record_id)
```

### 4. HTTP Server (`mcp_server_http.py`)

**Endpoints:**
- `GET /health` - Health check
- `GET /info` - Server info
- `GET /tools` - List tools
- `GET /tools/{name}` - Tool schema
- `POST /tools/call` - Execute tool
- `POST /mcp/initialize` - Initialize
- `POST /mcp/call` - Generic MCP call
- `POST /workflows/*` - Pre-built workflows
- `POST /agent/query` - Intelligent query
- `POST /batch/execute` - Batch operations

---

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```env
SF_USERNAME=your_username
SF_PASSWORD=your_password
SF_SECURITY_TOKEN=your_token
GEMINI_API_KEY=your_key
```

### 3. Run MCP Server (HTTP)
```bash
uvicorn mcp_server_http:app --reload --port 8000
```

### 4. Access API
- Interactive Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

---

## Usage Examples

### Example 1: Direct Tool Call via HTTP

```bash
curl -X POST "http://localhost:8000/tools/call" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "get_record",
    "arguments": {
      "object_type": "Account",
      "record_id": "001Xx000010SQA"
    }
  }'
```

### Example 2: Workflow Execution

```bash
curl -X POST "http://localhost:8000/workflows/enrich-record?object_type=Account&record_id=001Xx000010SQA"
```

### Example 3: Intelligent Agent Query

```bash
curl -X POST "http://localhost:8000/agent/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Get the Account record 001Xx000010SQA and show me a summary",
    "mode": "intelligent"
  }'
```

### Example 4: Batch Execution

```bash
curl -X POST "http://localhost:8000/batch/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "requests": [
      {
        "name": "summarize_record",
        "arguments": {"object_type": "Account", "record_id": "001Xx000010SQA"}
      },
      {
        "name": "get_record",
        "arguments": {"object_type": "Contact", "record_id": "003Xx000004TMA"}
      }
    ]
  }'
```

### Example 5: Python Client

```python
import asyncio
from mcp_client import MCPClient, MCPWorkflowBuilder
from mcp_server import MCPOrchestrator

async def main():
    orchestrator = MCPOrchestrator()
    client = MCPClient(orchestrator)
    await client.initialize()
    
    # Single tool
    result = await client.call_tool("get_record", {
        "object_type": "Account",
        "record_id": "001Xx000010SQA"
    })
    print(result)
    
    # Workflow
    builder = MCPWorkflowBuilder(client)
    builder.add_step("validate", "validate_update", {...})
    builder.add_step("update", "update_record", {...})
    result = await builder.execute()
    print(result)

asyncio.run(main())
```

### Example 6: Intelligent Agent

```python
import asyncio
from orchestrated_agent import OrchestrationAgent, AgentMode

async def main():
    agent = OrchestrationAgent(mode=AgentMode.INTELLIGENT)
    await agent.initialize()
    
    # Natural language query
    result = await agent.process_query(
        "Get the Account 001Xx000010SQA and tell me what it is"
    )
    print(result)
    
    # Specific workflow
    result = await agent.validate_and_update(
        "Account",
        "001Xx000010SQA",
        {"Phone": "+1-555-0100"}
    )
    print(result)

asyncio.run(main())
```

---

## Tool Definitions and Schemas

### get_record

**Purpose:** Retrieve a Salesforce record

**Parameters:**
- `object_type` (string, required): Salesforce object type
- `record_id` (string, required): Record ID
- `fields` (array, optional): Specific fields

**Returns:**
```json
{
  "status": "success",
  "full_record": {...},
  "summary": {...},
  "object_type": "Account",
  "record_id": "001Xx000010SQA"
}
```

### update_record

**Purpose:** Update record fields

**Parameters:**
- `object_type` (string, required): Object type
- `record_id` (string, required): Record ID
- `fields` (object, required): Fields to update

**Returns:**
```json
{
  "status": "success",
  "message": "Record updated successfully",
  "record_id": "001Xx000010SQA"
}
```

### summarize_record

**Purpose:** Get record summary

**Parameters:**
- `object_type` (string, required): Object type
- `record_id` (string, required): Record ID

**Returns:**
```json
{
  "id": "001Xx000010SQA",
  "type": "Account",
  "name": "Acme Corporation",
  "created_date": "2024-01-15T...",
  "last_modified": "2024-04-20T..."
}
```

### validate_update

**Purpose:** Validate proposed update

**Parameters:**
- `object_type` (string, required): Object type
- `record_id` (string, required): Record ID
- `fields` (object, required): Fields to validate

**Returns:**
```json
{
  "valid": true,
  "record_id": "001Xx000010SQA",
  "fields_to_update": 2,
  "warnings": ["Field exceeds length"]
}
```

---

## Workflow Types

### Pre-built Workflows

#### 1. Validate and Update
```python
await engine.validate_then_update_workflow(
    object_type="Account",
    record_id="001Xx000010SQA",
    fields={"Phone": "+1-555-0100"}
)
```

**Steps:**
1. Validate update
2. Update record (if valid)

#### 2. Enrich Record
```python
await engine.enrich_record_workflow(
    object_type="Account",
    record_id="001Xx000010SQA"
)
```

**Steps:**
1. Get full record
2. Get record summary

### Custom Workflows

```python
builder = MCPWorkflowBuilder(client)
builder.add_step("step1", "tool1", {"arg": "value"})
builder.add_step("step2", "tool2", {"arg": "value"})
result = await builder.execute()
```

---

## Request/Response Format

### Tool Call Request (MCP)
```json
{
  "method": "tools/call",
  "params": {
    "name": "get_record",
    "arguments": {
      "object_type": "Account",
      "record_id": "001Xx000010SQA"
    }
  },
  "id": "request-id-123"
}
```

### Tool Call Response (MCP)
```json
{
  "jsonrpc": "2.0",
  "id": "request-id-123",
  "result": {
    "status": "success",
    "tool": "get_record",
    "result": {...}
  }
}
```

---

## Error Handling

### Tool Not Found
```json
{
  "status": "error",
  "error": "Tool 'unknown_tool' not found",
  "available_tools": ["get_record", "update_record", ...]
}
```

### Invalid Parameters
```json
{
  "status": "error",
  "error": "Invalid parameters: ...",
  "tool": "get_record"
}
```

### Execution Error
```json
{
  "status": "error",
  "error": "Record not found"
}
```

---

## Production Deployment

### Using Docker

```dockerfile
FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "mcp_server_http:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Using Gunicorn

```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker mcp_server_http:app
```

---

## Monitoring and Logging

### Access Logs
```bash
tail -f logs/mcp_server.log
```

### Check Health
```bash
curl http://localhost:8000/health
```

### View History
```bash
curl http://localhost:8000/agent/history
```

---

## Best Practices

1. **Always validate before updates** - Use `validate_update` first
2. **Use workflows for complex operations** - Sequence related tools
3. **Handle errors gracefully** - Check response status
4. **Cache tool definitions** - List tools once, use many times
5. **Monitor execution history** - Track tool usage
6. **Use batch operations** - For multiple independent calls
7. **Set appropriate timeouts** - For remote calls

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Connection refused | Check server is running on port 8000 |
| Tool not found | Verify tool name in available tools |
| Invalid parameters | Check parameter types in tool schema |
| Record not found | Verify 18-character Salesforce IDs |
| Auth errors | Check .env credentials |

---

## References

- [MCP Specification](https://modelcontextprotocol.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Salesforce API Reference](https://developer.salesforce.com/docs/api/)
- [OpenAPI/Swagger](https://swagger.io/)

---

## Support

For issues or questions:
1. Check `/docs` endpoint for interactive documentation
2. Review execution history with `/agent/history`
3. Test tools individually via `/tools/call`
4. Check server logs for error details

**Server is ready for production use!** 🚀
