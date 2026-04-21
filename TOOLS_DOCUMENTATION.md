# Salesforce MCP Agent - Tools Documentation

## Overview

This enhanced Salesforce MCP Agent now includes four specialized tools orchestrated through LangGraph for intelligent workflow management.

## Tools

### 1. **get_record**
Retrieve a Salesforce record by ID with optional field selection.

**Function Signature:**
```python
get_record_tool(object_type: str, record_id: str, fields: Optional[list] = None) -> Dict[str, Any]
```

**Parameters:**
- `object_type` (str): Salesforce object type (e.g., "Account", "Contact", "Opportunity")
- `record_id` (str): The record ID to retrieve
- `fields` (list, optional): Specific fields to retrieve

**Example Usage:**
```python
from tools import get_record_tool

# Get entire record
result = get_record_tool("Account", "001Xx000010SQA")

# Get specific fields
result = get_record_tool("Contact", "003Xx000004TMA", fields=["Name", "Email", "Phone"])
```

**Returns:**
```json
{
  "Id": "001Xx000010SQA",
  "Name": "Acme Corporation",
  "BillingCity": "San Francisco",
  ...
}
```

---

### 2. **update_record**
Update Salesforce record with new field values.

**Function Signature:**
```python
update_record_tool(object_type: str, record_id: str, fields: Dict[str, Any]) -> Dict[str, Any]
```

**Parameters:**
- `object_type` (str): Salesforce object type
- `record_id` (str): The record ID to update
- `fields` (dict): Dictionary of fields and values to update

**Example Usage:**
```python
from tools import update_record_tool

result = update_record_tool(
    "Account",
    "001Xx000010SQA",
    {
        "BillingCity": "New York",
        "Phone": "+1-212-555-0100",
        "Website": "https://acme.example.com"
    }
)
```

**Returns:**
```json
{
  "status": "success",
  "message": "Record 001Xx000010SQA updated successfully",
  "record_id": "001Xx000010SQA"
}
```

---

### 3. **summarize_record**
Retrieve and summarize a record's key information.

**Function Signature:**
```python
summarize_record_tool(object_type: str, record_id: str) -> Dict[str, Any]
```

**Parameters:**
- `object_type` (str): Salesforce object type
- `record_id` (str): The record ID to summarize

**Example Usage:**
```python
from tools import summarize_record_tool

summary = summarize_record_tool("Opportunity", "006Xx000001SVPA")
```

**Returns:**
```json
{
  "id": "006Xx000001SVPA",
  "type": "Opportunity",
  "name": "Acme - 100 Licenses",
  "created_date": "2024-01-15T10:30:00.000+0000",
  "last_modified": "2024-04-20T14:22:15.000+0000"
}
```

---

### 4. **validate_update**
Validate a proposed update before applying it to detect potential issues.

**Function Signature:**
```python
validate_update_tool(object_type: str, record_id: str, fields: Dict[str, Any]) -> Dict[str, Any]
```

**Parameters:**
- `object_type` (str): Salesforce object type
- `record_id` (str): The record ID to validate
- `fields` (dict): Dictionary of fields proposed for update

**Example Usage:**
```python
from tools import validate_update_tool

validation = validate_update_tool(
    "Account",
    "001Xx000010SQA",
    {
        "LongDescription": "This is a very long description..." * 100,  # Very long
        "AccountNumber": "123456"
    }
)
```

**Returns:**
```json
{
  "valid": true,
  "record_id": "001Xx000010SQA",
  "fields_to_update": 2,
  "warnings": [
    "Field 'LongDescription' exceeds recommended length"
  ]
}
```

**Validation Checks:**
- Record existence validation
- System field warnings
- Text length validation (max 4000 chars recommended)

---

## Tool Registry

All tools are registered in the `TOOLS` dictionary for MCP integration:

```python
from tools import TOOLS

TOOLS = {
    "get_record": get_record_tool,
    "update_record": update_record_tool,
    "summarize_record": summarize_record_tool,
    "validate_update": validate_update_tool,
}
```

---

## LangGraph Workflow Integration

### Architecture

The MCP agent uses LangGraph to create a stateful workflow:

```
┌─────────────────┐
│  process_input  │
└────────┬────────┘
         │
    ┌────▼─────┐
    │  Router  │
    └┬───┬───┬─┘
     │   │   │
     ▼   ▼   ▼
   tool clarify response
  execute
     │
     └─────┬──────┘
          │
     ┌────▼─────┐
     │  respond │
     └──────────┘
```

### State Management

**AgentState** defines the workflow state:

```python
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]      # User messages
    tool_calls: list                              # Pending tool calls
    tool_results: list                            # Tool execution results
    final_response: str                           # Final agent response
    current_action: Optional[str]                 # Current workflow action
```

### Node Functions

1. **process_input_node**: Analyzes user input and decides next action
2. **tool_executor_node**: Executes requested tools with error handling
3. **clarify_node**: Handles requests for clarification
4. **respond_node**: Formats final response

---

## Usage Patterns

### Pattern 1: Simple Query
```python
from agent import handle_query

response = handle_query("Get the Account record 001Xx000010SQA")
print(response)
```

### Pattern 2: Update with Validation
```python
from agent import handle_query_with_validation

result = handle_query_with_validation(
    "Update Account 001Xx000010SQA with new phone +1-555-0100"
)
print(result["response"])
if "validation" in result:
    print("Validation:", result["validation"])
```

### Pattern 3: Direct Tool Usage
```python
from tools import TOOLS

# Get record
record = TOOLS["get_record"]("Account", "001Xx000010SQA")

# Validate before updating
validation = TOOLS["validate_update"](
    "Account",
    "001Xx000010SQA",
    {"Phone": "+1-555-0100"}
)

if validation["valid"]:
    result = TOOLS["update_record"](
        "Account",
        "001Xx000010SQA",
        {"Phone": "+1-555-0100"}
    )
```

---

## Error Handling

All tools include comprehensive error handling:

```python
{
  "status": "error",
  "message": "Failed to get record: [error details]"
}
```

or

```python
{
  "valid": False,
  "error": "Record not found"
}
```

---

## Environment Variables

Required in `.env`:
```
SF_USERNAME=your_salesforce_username
SF_PASSWORD=your_salesforce_password
SF_SECURITY_TOKEN=your_security_token
GEMINI_API_KEY=your_gemini_api_key
```

---

## Running the Application

### Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run Streamlit app
streamlit run app.py
```

### Testing Tools Directly
```bash
python -c "
from tools import TOOLS
result = TOOLS['get_record']('Account', 'YOUR_RECORD_ID')
print(result)
"
```

---

## Tips & Best Practices

1. **Always validate before updates**: Use `validate_update` before `update_record`
2. **Use field selection**: Specify fields in `get_record` to reduce data transfer
3. **Handle errors gracefully**: Check for "error" or "valid" keys in responses
4. **Batch operations**: Use LangGraph workflow for multiple related operations
5. **Monitor warnings**: Pay attention to validation warnings for data integrity

---

## Support & Troubleshooting

- **Connection Issues**: Verify Salesforce credentials and security token
- **Tool Not Found**: Check that all tools are registered in the TOOLS dictionary
- **Invalid Records**: Ensure record IDs are properly formatted (18-character IDs)
- **LangGraph Errors**: Check Python version (3.8+) and all dependencies installed
