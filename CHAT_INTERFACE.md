# CHAT_INTERFACE.md
# Chat Interface User Guide

## Overview

The Salesforce MCP Agent now includes a **professional chat interface** with:
- ✅ Persistent session management
- ✅ Full conversation history
- ✅ Tool orchestration
- ✅ Export capabilities
- ✅ Real-time interactions
- ✅ Validation workflows

## Features

### 1. **Session Management**
- **Automatic saving**: Conversations are automatically saved
- **Session history**: Access previous conversations
- **Session restoration**: Resume any past conversation
- **New chat**: Start fresh conversations anytime

### 2. **Conversation Tracking**
Each conversation tracks:
- User messages and agent responses
- Tools used and their results
- Timestamps for all interactions
- Session metadata (created, updated times)

### 3. **Tool Orchestration**
The agent automatically:
- Decides which tool to use based on your request
- Validates updates before executing them
- Handles errors gracefully
- Provides detailed feedback

### 4. **Export Options**
Export conversations as:
- **JSON**: Full data structure with all metadata
- **Markdown**: Readable formatted text
- **Text**: Plain text format

### 5. **Query Modes**

#### Standard Mode
- Direct tool execution
- Fast processing
- Suitable for simple queries

#### With Validation Mode
- Automatic validation before updates
- Safety checks for data integrity
- Recommended for production changes

## Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Create `.env` file:
```env
SF_USERNAME=your_salesforce_username
SF_PASSWORD=your_salesforce_password
SF_SECURITY_TOKEN=your_security_token
GEMINI_API_KEY=your_gemini_api_key
```

### 3. Run the Chat Interface
```bash
streamlit run chat_app.py
```

The app will open at `http://localhost:8501`

## Usage Examples

### Example 1: Get Record Information
```
User: Get the Account record 001Xx000010SQA
```

**Response:**
```
✅ Record Retrieved:
- ID: 001Xx000010SQA
- Type: Account
- Name: Acme Corporation
- Created: 2024-01-15T10:30:00
- Last Modified: 2024-04-20T14:22:15
```

### Example 2: Summarize a Record
```
User: Summarize the Contact 003Xx000004TMA
```

**Response:**
```
✅ Record Summary:
- ID: 003Xx000004TMA
- Type: Contact
- Name: John Smith
- Created: 2024-02-01
```

### Example 3: Update with Validation
```
User: Update Account 001Xx000010SQA with phone +1-212-555-0100
```

**Response (With Validation Mode):**
```
⚠️ Validation performed:
- Fields to update: 1
- Warnings: None

✅ Record Updated - Record 001Xx000010SQA updated successfully
```

### Example 4: Check for Issues
```
User: Is it safe to update the Account phone field?
```

**Response:**
```
✅ Validation Result: Valid
- Fields to update: 1
- Warnings: None
```

## UI Components

### Left Sidebar
- **Current Session Info**: Active session details
- **New Chat Button**: Create new conversation
- **Clear Button**: Clear current conversation
- **History Panel**: Browse previous conversations
- **Export Options**: Download conversations
- **Settings**: Configure query mode and view tools
- **Help**: Usage examples and tips

### Main Chat Area
- **Conversation Display**: All messages and tool results
- **Input Field**: Type your requests
- **Send Button**: Submit your message
- **Tool Details**: View detailed tool execution info
- **Quick Actions**: Quick action buttons

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Send Message | Enter (in text field) |
| New Chat | See sidebar button |
| Export | Use sidebar export section |
| Clear | See sidebar button |

## Session Management

### Create New Session
```
Click "➕ New Chat" button in sidebar
```

### Load Previous Session
```
Click on any session in the History panel
```

### Delete Session
```
Click "×" button next to session name
```

### Export Session
```
1. Select export format (JSON/Markdown/Text)
2. Click "📥 Export Current Chat"
3. Click download button
```

## Session Data Structure

Sessions are stored as JSON with:
```json
{
  "session_id": "session_20240421_120000_1",
  "title": "New Chat",
  "created_at": "2024-04-21T12:00:00",
  "updated_at": "2024-04-21T12:05:30",
  "messages": [
    {
      "role": "user|assistant",
      "content": "message text",
      "timestamp": "2024-04-21T12:00:01",
      "tool_info": {...}
    }
  ],
  "metadata": {
    "status": "active",
    "message_count": 5,
    "tool_calls": 2
  }
}
```

## Settings & Configuration

### Query Mode Selection
- **Standard**: Fast, direct tool execution
- **With Validation**: Includes validation before updates

### Tool Registry
View available tools in settings:
- `get_record`: Fetch Salesforce records
- `update_record`: Modify records
- `summarize_record`: Quick summary
- `validate_update`: Pre-flight checks

## Troubleshooting

### Issue: Session Not Saving
**Solution**: Ensure `.sessions` directory has write permissions
```bash
chmod 755 .sessions
```

### Issue: Tools Not Available
**Solution**: Verify dependencies installed
```bash
pip install -r requirements.txt
```

### Issue: Salesforce Connection Error
**Solution**: Check `.env` credentials
```bash
# Verify SFDX login
sfdx auth:list
```

### Issue: Chat Not Loading Previous Sessions
**Solution**: Check session files are in `.sessions` directory
```bash
ls -la .sessions/
```

## Session Storage

Sessions are stored in `.sessions/` directory as individual JSON files:
```
.sessions/
├── session_20240421_120000_1.json
├── session_20240420_150030_2.json
└── session_20240420_100000_3.json
```

## Best Practices

### For Better Interactions
1. ✅ Be specific with record IDs
2. ✅ Use natural language
3. ✅ Check validation warnings
4. ✅ Export important conversations
5. ✅ Review tool details for debugging

### For Data Integrity
1. ✅ Always use "With Validation" for updates
2. ✅ Review warnings before confirming
3. ✅ Keep backups of exported sessions
4. ✅ Test with non-critical data first

## API Integration

### Using Session Manager Programmatically
```python
from session_manager import SessionManager

# Initialize
sm = SessionManager()

# Create session
session_id = sm.create_session("My Session")

# Add messages
sm.add_user_message("Get Account 001Xx000010SQA")
sm.add_assistant_message("Record retrieved successfully")

# Export
exported = sm.export_session(session_id, format="json")

# List sessions
sessions = sm.list_sessions()
```

### Using MCP Orchestrator Programmatically
```python
from mcp_orchestrator import process_mcp_request

# Process request
result = process_mcp_request("Get Account 001Xx000010SQA")

# Check results
print(result["messages"])
print(result["tool_calls"])
print(result["success"])
```

## Advanced Features

### Multi-Tool Workflows
The orchestrator automatically handles complex workflows like:
1. Validate update parameters
2. Execute update if valid
3. Return results and warnings

### Context Management
Sessions maintain context across messages:
- Previous tool results
- User intent
- Execution history
- Validation states

### Analytics & Monitoring
Track usage statistics:
- Total messages in session
- Tools used
- Success/failure rates
- Execution history

## Support & Help

For issues or questions:
1. Check Help section in sidebar
2. Review CHAT_INTERFACE.md (this file)
3. See TOOLS_DOCUMENTATION.md for tool details
4. Check example scripts in examples.py

## Next Steps

1. 🚀 **Run the app**: `streamlit run chat_app.py`
2. 📚 **Explore examples**: See sidebar for sample queries
3. 📊 **Track conversations**: Use history panel
4. 💾 **Export & backup**: Export important chats
5. ⚙️ **Customize**: Adjust settings to your preference

---

**Enjoy your enhanced Salesforce MCP chat experience! 🎉**
