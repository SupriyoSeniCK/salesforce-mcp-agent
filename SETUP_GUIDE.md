# SETUP_GUIDE.md
# Chat Interface Setup Guide

## Quick Setup (5 minutes)

### Step 1: Install Dependencies
```bash
cd /Users/supriyoseni/Documents/salesforce-mcp-agent
pip install -r requirements.txt
```

### Step 2: Verify Environment
Ensure `.env` file exists with:
```env
SF_USERNAME=your_salesforce_username
SF_PASSWORD=your_salesforce_password
SF_SECURITY_TOKEN=your_salesforce_security_token
GEMINI_API_KEY=your_gemini_api_key
```

### Step 3: Run the Chat App
```bash
streamlit run chat_app.py
```

The app will open automatically at: **http://localhost:8501**

## What You Get

### 📱 Chat Interface
```
┌─────────────────────────────────────────────────────────┐
│         💬 Salesforce MCP Chat Agent                    │
├─────────────────┬───────────────────────────────────────┤
│                 │                                       │
│  📋 Sidebar     │    💭 Chat Display                   │
│  • New Chat     │    ┌─────────────────────────────┐   │
│  • History      │    │ User: Get Account 001...    │   │
│  • Sessions     │    ├─────────────────────────────┤   │
│  • Export       │    │ Agent: ✅ Record Retrieved  │   │
│  • Settings     │    └─────────────────────────────┘   │
│                 │                                       │
│                 │  📝 Input: [Your message here] 📤    │
│                 │                                       │
└─────────────────┴───────────────────────────────────────┘
```

## File Structure

```
Created Files:
├── chat_app.py                 ✨ NEW - Main chat interface
├── session_manager.py          ✨ NEW - Session persistence
├── mcp_orchestrator.py         ✨ NEW - Tool orchestration
├── CHAT_INTERFACE.md           ✨ NEW - Chat guide
├── README_CHAT.md              ✨ NEW - Comprehensive README
└── SETUP_GUIDE.md              ✨ NEW - This file

Updated Files:
├── .sessions/                  📁 NEW - Session storage
├── llm.py                      🔄 Enhanced with LangGraph
├── agent.py                    🔄 New handler functions
├── tools.py                    🔄 Added orchestration
├── state.py                    🔄 Updated state management
└── requirements.txt            🔄 New dependencies
```

## Key Components

### 1. **Session Manager** (`session_manager.py`)
Handles all conversation persistence:
- Create sessions
- Save messages
- Restore conversations
- Export in multiple formats

**Usage:**
```python
from session_manager import SessionManager

sm = SessionManager()
session_id = sm.create_session("My Chat")
sm.add_user_message("Get Account 001Xx000010SQA")
sm.add_assistant_message("Record retrieved successfully")
```

### 2. **MCP Orchestrator** (`mcp_orchestrator.py`)
Manages tool execution and workflows:
- Route requests to tools
- Validate operations
- Track execution
- Format results

**Usage:**
```python
from mcp_orchestrator import process_mcp_request

result = process_mcp_request("Get Account 001Xx000010SQA")
print(result['messages'])
print(result['success'])
```

### 3. **Chat App** (`chat_app.py`)
Professional Streamlit interface:
- Real-time chat display
- Session management
- Tool execution
- Export capabilities

**Run:**
```bash
streamlit run chat_app.py
```

## Quick-Start Example

### Scenario: Get and Update an Account

1. **Start the app:**
   ```bash
   streamlit run chat_app.py
   ```

2. **Type in chat:**
   ```
   Get the Account record 001Xx000010SQA
   ```

3. **View result:**
   ```
   ✅ Record Retrieved:
   - ID: 001Xx000010SQA
   - Type: Account
   - Name: Acme Corporation
   ```

4. **Continue conversation:**
   ```
   Update the phone to +1-212-555-0100
   ```

5. **Agent validates and updates:**
   ```
   ⚠️ Validation performed
   ✅ Record Updated - Success
   ```

6. **Export conversation:**
   - Use sidebar "Export" button
   - Download as JSON, Markdown, or Text

## Architecture Overview

### Data Flow
```
User Input
    ↓
[Chat App] (Streamlit UI)
    ↓
[Session Manager] (Save user message)
    ↓
[MCP Orchestrator] (Route request)
    ↓
[LLM] (Understand intent)
    ↓
[Tool Selector] (Choose tool)
    ↓
[Validation] (Pre-flight checks)
    ↓
[Tool Executor] (Execute tool)
    ↓
[Result Formatter] (Format response)
    ↓
[Session Manager] (Save response)
    ↓
[Chat App] (Display to user)
```

### Session Storage
Sessions are stored locally in `.sessions/` directory:
```
.sessions/
├── session_20240421_120000_1.json
├── session_20240420_150030_2.json
└── session_20240420_100000_3.json
```

Each session contains:
- Session ID and title
- All messages (user & assistant)
- Tool execution info
- Timestamps
- Metadata

## Configuration

### Environment Variables (`.env`)
```env
# Salesforce
SF_USERNAME=your_salesforce_email@company.com
SF_PASSWORD=your_salesforce_password
SF_SECURITY_TOKEN=your_security_token

# Gemini AI
GEMINI_API_KEY=your_gemini_api_key

# Optional
STREAMLIT_SERVER_PORT=8501
```

### Streamlit Config (`~/.streamlit/config.toml`)
```toml
[client]
showErrorDetails = true

[server]
maxUploadSize = 10
```

## Usage Patterns

### Pattern 1: Simple Query
```python
# User types: "Get Account 001Xx000010SQA"
# Agent automatically:
# 1. Understands intent
# 2. Selects get_record tool
# 3. Fetches and summarizes
# 4. Returns formatted result
```

### Pattern 2: Update with Validation
```python
# User types: "Update Account phone to +1-555-0100"
# Agent automatically:
# 1. Validates the update
# 2. Checks for issues
# 3. Displays warnings (if any)
# 4. Executes update
# 5. Confirms success
```

### Pattern 3: Conversation Context
```python
# Message 1: "Get Account 001Xx000010SQA"
# Message 2: "What's the revenue?" (uses context from message 1)
# Message 3: "Update it to 5000000"
# Agent maintains context across messages
```

## Troubleshooting

### Dependencies Not Installed
```bash
# Solution: Install requirements
pip install -r requirements.txt

# Or specific packages
pip install streamlit langgraph simple-salesforce google-genai
```

### Salesforce Connection Error
```bash
# Check credentials in .env
# Verify with SFDX
sfdx auth:list

# Reset security token
# (In Salesforce: Settings > Security > Reset Security Token)
```

### Streamlit Port Already in Use
```bash
# Use different port
streamlit run chat_app.py --server.port 8502
```

### Sessions Not Loading
```bash
# Check folder permissions
ls -la .sessions/

# Or recreate folder
mkdir -p .sessions
chmod 755 .sessions
```

## Testing

### Test 1: Basic Import
```bash
python3 -c "from chat_app import *; print('✅ Chat app OK')"
```

### Test 2: Session Manager
```bash
python3 << 'EOF'
from session_manager import SessionManager
sm = SessionManager()
sid = sm.create_session("Test")
sm.add_user_message("Test message")
print(f"✅ Session created: {sid}")
EOF
```

### Test 3: MCP Orchestrator
```bash
python3 << 'EOF'
from mcp_orchestrator import MCPOrchestrator
orch = MCPOrchestrator()
print(f"✅ Orchestrator OK")
EOF
```

### Test 4: Run Full App
```bash
streamlit run chat_app.py
# Then interact with the UI
```

## Performance Tips

1. **Use "With Validation" mode** for production
2. **Specify fields** in get_record for large objects
3. **Export sessions** regularly for backup
4. **Monitor sidebar stats** for usage patterns
5. **Clear old sessions** periodically

## Next Steps

1. ✅ Install dependencies: `pip install -r requirements.txt`
2. ✅ Configure `.env` with your credentials
3. ✅ Run the app: `streamlit run chat_app.py`
4. ✅ Try example queries (see Help in sidebar)
5. ✅ Export and backup important chats
6. ✅ Read [CHAT_INTERFACE.md](CHAT_INTERFACE.md) for full guide

## Support Resources

| Resource | Purpose |
|----------|---------|
| [README_CHAT.md](README_CHAT.md) | Full feature guide |
| [CHAT_INTERFACE.md](CHAT_INTERFACE.md) | Detailed instructions |
| [TOOLS_DOCUMENTATION.md](TOOLS_DOCUMENTATION.md) | Tool API reference |
| [QUICKSTART.md](QUICKSTART.md) | Quick reference |
| examples.py | Code samples |

## Common Commands

```bash
# Start chat interface
streamlit run chat_app.py

# Test session manager
python3 -c "from session_manager import SessionManager; SessionManager()"

# Install dependencies
pip install -r requirements.txt

# View sessions
ls -la .sessions/

# Clear sessions
rm -rf .sessions/

# Run on custom port
streamlit run chat_app.py --server.port 8502
```

## Keyboard Shortcuts

| Action | Method |
|--------|--------|
| Send Message | Type and click button |
| New Chat | Click "➕ New Chat" sidebar |
| Clear Current | Click "🗑️ Clear" sidebar |
| Export | Use "⬇️ Export" section |
| View Help | Click "❓ Help" sidebar |

---

## You're All Set! 🎉

Your Salesforce MCP Chat Agent is ready to use!

**Quick start:**
```bash
streamlit run chat_app.py
```

Then start asking questions about your Salesforce data! 💬

For detailed information, see [CHAT_INTERFACE.md](CHAT_INTERFACE.md)
