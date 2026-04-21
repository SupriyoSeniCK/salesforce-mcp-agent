# Enhanced Salesforce MCP Agent - Quick Reference

## 🎯 What's New

### ✨ New Tools Added
Your agent now includes 4 specialized, composable tools:

| Tool | Purpose | Key Use Case |
|------|---------|--------------|
| **get_record** | Retrieve records with optional field selection | Fetch account/contact details |
| **update_record** | Update record fields with validation support | Modify field values |
| **summarize_record** | Get key record information quickly | Overview without all details |
| **validate_update** | Pre-flight checks before updates | Prevent errors and data issues |

### 🔄 LangGraph Integration
Your agent now uses LangGraph for intelligent workflow orchestration:
- Stateful message handling
- Automatic routing between tools
- Built-in error handling
- Validation workflows

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up Environment
Create `.env` file:
```env
SF_USERNAME=your_username
SF_PASSWORD=your_password
SF_SECURITY_TOKEN=your_token
GEMINI_API_KEY=your_key
```

### 3. Run the App
```bash
# Streamlit UI
streamlit run app.py

# Run examples
python examples.py --all
```

---

## 📖 Usage Examples

### Direct Tool Usage
```python
from tools import TOOLS

# Get a record
account = TOOLS['get_record']('Account', '001Xx000010SQA', fields=['Name', 'Phone'])

# Validate an update first
validation = TOOLS['validate_update']('Account', '001Xx000010SQA', {'Phone': '+1-555-0100'})

if validation['valid']:
    result = TOOLS['update_record']('Account', '001Xx000010SQA', {'Phone': '+1-555-0100'})

# Summarize a record
summary = TOOLS['summarize_record']('Opportunity', '006Xx000001SVPA')
```

### LangGraph Workflow
```python
from agent import handle_query, handle_query_with_validation

# Simple query - LLM chooses tool
response = handle_query("Get the Account 001Xx000010SQA")

# Query with validation
result = handle_query_with_validation("Update Account 001Xx000010SQA phone to +1-555-0100")
```

### Streamlit UI
```bash
streamlit run app.py
```

---

## 🏗️ Architecture

### MCP Workflow Flow
```
User Input
    ↓
[Process Input] → LLM Decision
    ↓
    ├→ Tool Call → [Execute Tool] → Tool Results
    ├→ Clarification → [Ask User]
    └→ Response → [Generate Response]
    ↓
Final Response to User
```

### Tool Registry
```python
TOOLS = {
    "get_record": get_record_tool,
    "update_record": update_record_tool,
    "summarize_record": summarize_record_tool,
    "validate_update": validate_update_tool,
}
```

---

## 📁 File Structure

```
salesforce-mcp-agent/
├── tools.py                    # ✨ NEW: 4 specialized tools
├── llm.py                      # 🔄 UPDATED: LangGraph integration
├── agent.py                    # 🔄 UPDATED: New workflow handlers
├── app.py                      # 🔄 UPDATED: Enhanced Streamlit UI
├── state.py                    # 🔄 UPDATED: LangGraph state management
├── examples.py                 # ✨ NEW: Usage examples & demos
├── TOOLS_DOCUMENTATION.md      # ✨ NEW: Comprehensive tool docs
├── requirements.txt            # 🔄 UPDATED: Dependencies
└── README.md                   # Project setup guide
```

---

## 🔧 Tool API Reference

### get_record
```python
get_record_tool(
    object_type: str,           # 'Account', 'Contact', etc
    record_id: str,             # 18-char Salesforce ID
    fields: Optional[list] = None  # ['Name', 'Phone', ...]
) → Dict[str, Any]
```

### update_record
```python
update_record_tool(
    object_type: str,
    record_id: str,
    fields: Dict[str, Any]      # {'Phone': '+1-555-0100', ...}
) → Dict[str, Any]
```

### summarize_record
```python
summarize_record_tool(
    object_type: str,
    record_id: str
) → Dict[str, Any]  # {id, type, name, created_date, last_modified}
```

### validate_update
```python
validate_update_tool(
    object_type: str,
    record_id: str,
    fields: Dict[str, Any]
) → Dict[str, Any]  # {valid: bool, warnings: list, ...}
```

---

## 🎓 Best Practices

### ✓ Do's
- ✓ Always validate before updating: `validate_update` → `update_record`
- ✓ Use field selection in `get_record` to reduce data transfer
- ✓ Handle error keys in responses: check for "error" or "valid"
- ✓ Use LangGraph workflow for complex multi-step operations
- ✓ Monitor and act on validation warnings

### ✗ Don'ts
- ✗ Don't skip validation for production updates
- ✗ Don't ignore error responses
- ✗ Don't fetch all fields when you only need a few
- ✗ Don't hardcode record IDs - make them dynamic

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: langgraph` | Run `pip install -r requirements.txt` |
| Salesforce connection fails | Check `.env` credentials and security token |
| Tool not found error | Verify tool name in TOOLS dictionary |
| Record not found | Ensure 18-character record ID format |
| LangGraph import error | Ensure Python 3.8+ with `typing-extensions` |

---

## 📚 Additional Resources

- [Full Tool Documentation](TOOLS_DOCUMENTATION.md)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Salesforce API Reference](https://developer.salesforce.com/docs/api/)
- [Examples Script](examples.py)

---

## 🎯 Next Steps

1. **Test Tools**: Run `python examples.py --test-tools`
2. **Review Examples**: Check `python examples.py --all`
3. **Run UI**: Execute `streamlit run app.py`
4. **Read Docs**: See [TOOLS_DOCUMENTATION.md](TOOLS_DOCUMENTATION.md)
5. **Integrate**: Use tools in your application!

---

## 💡 Use Cases

### Use Case 1: Real-time Account Status
```python
# Get account info
account = TOOLS['get_record']('Account', account_id, ['Status', 'Revenue'])

# Summarize for display
summary = TOOLS['summarize_record']('Account', account_id)
```

### Use Case 2: Safe Updates with Validation
```python
# Natural language instruction
result = handle_query_with_validation(
    "Update Account with new billing address"
)
# Validation happens automatically!
```

### Use Case 3: Data Quality Checks
```python
# Check before bulk operations
validation = TOOLS['validate_update'](obj_type, record_id, updates)
if not validation['valid']:
    print(f"Cannot update: {validation['error']}")
```

---

## 📞 Support

For issues or questions:
1. Check TOOLS_DOCUMENTATION.md for detailed API info
2. Run examples.py for working code samples
3. Review Streamlit UI output for errors
4. Verify Salesforce connection in .env

---

**Happy coding! 🚀**
