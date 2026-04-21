# Salesforce MCP Agent with Chat Interface

A professional **Model Context Protocol (MCP) agent** for Salesforce with an advanced chat interface, session management, and tool orchestration.

## ✨ Key Features

### 🎯 Core Features
- **🤖 Intelligent Agent**: LLM-powered decision making for tool selection
- **💬 Chat Interface**: Professional conversation UI with history
- **💾 Session Management**: Persistent conversation storage and retrieval
- **🔧 Tool Orchestration**: Automated tool selection and execution
- **✅ Validation Framework**: Pre-flight checks for safe operations
- **📊 Analytics**: Track tool usage and execution history

### 🛠️ Available Tools
1. **get_record** - Retrieve Salesforce records with optional field selection
2. **update_record** - Update records with status confirmation
3. **summarize_record** - Get key record information quickly
4. **validate_update** - Pre-flight validation to prevent errors

### 💻 Technologies
- **Streamlit**: Professional chat UI
- **LangGraph**: Workflow orchestration
- **Google Generative AI (Gemini)**: LLM for intent understanding
- **Simple Salesforce**: Salesforce API integration
- **Python 3.8+**: Core language

## 🚀 Quick Start

### 1. Clone & Setup
```bash
git clone <your-repo>
cd salesforce-mcp-agent
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
Create `.env` file in root directory:
```env
# Salesforce Configuration
SF_USERNAME=your_salesforce_username
SF_PASSWORD=your_salesforce_password
SF_SECURITY_TOKEN=your_salesforce_security_token

# Gemini AI Configuration
GEMINI_API_KEY=your_gemini_api_key
```

**Getting credentials:**
- **Salesforce**: Use your SFDX credentials
- **Gemini API**: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
- **Security Token**: Generate in Salesforce Settings > Security > Reset Security Token

### 4. Run the Chat Application
```bash
streamlit run chat_app.py
```

The application will open at `http://localhost:8501`

## 📖 Usage Guide

### Basic Workflow

1. **Type your request** in the chat input
2. **Agent analyzes** your request
3. **Selects appropriate tool(s)**
4. **Executes with validation** (in With Validation mode)
5. **Returns results** with detailed feedback

### Example Queries

**Get Record:**
```
Get the Account record 001Xx000010SQA
```

**Update Record:**
```
Update Account 001Xx000010SQA with phone +1-212-555-0100
```

**Summarize Record:**
```
Summarize the Contact 003Xx000004TMA
```

**Validate Update:**
```
Is it safe to update Account 001Xx000010SQA?
```

## 📁 Project Structure

```
salesforce-mcp-agent/
├── chat_app.py                 # Main chat interface (Streamlit)
├── session_manager.py          # Session persistence & management
├── mcp_orchestrator.py         # Tool orchestration & MCP logic
├── agent.py                    # Agent logic & tool execution
├── llm.py                      # LLM integration & LangGraph
├── tools.py                    # Salesforce tools definitions
├── state.py                    # State management
├── .env                        # Configuration (create this)
├── .sessions/                  # Session storage (auto-created)
├── requirements.txt            # Python dependencies
├── QUICKSTART.md               # Quick reference guide
├── TOOLS_DOCUMENTATION.md      # Detailed tool documentation
├── CHAT_INTERFACE.md           # Chat interface guide
└── README.md                   # This file
```

## 🎮 Features Guide

### Session Management
- **New Chat**: Create fresh conversation anytime
- **History**: Browse and restore previous conversations
- **Export**: Download chats as JSON, Markdown, or Text
- **Clear**: Reset current conversation

### Query Modes
- **Standard**: Direct tool execution
- **With Validation**: Includes pre-execution validation checks

### Tool Details
Click "🔧 Tool Details" to see:
- Tool execution status
- Parameters used
- Validation results
- Full response details

## 🔐 Security Considerations

1. **Credentials**: Never commit `.env` to version control
2. **Validation**: Always use "With Validation" mode for production
3. **Audit Trail**: Export sessions for compliance records
4. **Session Storage**: Sessions stored locally in `.sessions/`
5. **API Keys**: Rotate security tokens regularly

## 📊 Architecture

### Workflow Flow
```
User Input (Chat)
      ↓
  [Session Manager] (Save input)
      ↓
  [MCP Orchestrator] (Route request)
      ↓
  [LLM Decision] (Understand intent)
      ↓
  Tool Selection ← [Tool Registry]
      ↓
  [Validation] (Pre-flight checks)
      ↓
  Tool Execution
      ↓
  [Result Formatting]
      ↓
  [Session Manager] (Save response)
      ↓
  Display to User
```

### Components

**Session Manager** (`session_manager.py`)
- Persists conversations to disk
- Manages session lifecycle
- Provides conversation history
- Exports sessions in multiple formats

**MCP Orchestrator** (`mcp_orchestrator.py`)
- Routes requests to appropriate tools
- Manages validation workflows
- Tracks tool execution
- Provides execution analytics

**Chat App** (`chat_app.py`)
- Streamlit UI for conversations
- Sidebar for session management
- Real-time message display
- Quick action buttons

**LLM Integration** (`llm.py`)
- LangGraph workflow definition
- Intent understanding
- Tool selection logic
- Message formatting

**Tools** (`tools.py`)
- get_record: Fetch records
- update_record: Modify records
- summarize_record: Quick summaries
- validate_update: Pre-flight checks

## 🧪 Testing

### Test Direct Tool Usage
```python
from tools import TOOLS

# Test get_record
result = TOOLS['get_record']('Account', '001Xx000010SQA')
print(result)

# Test validation
validation = TOOLS['validate_update']('Account', '001Xx000010SQA', {'Phone': '+1-555-0100'})
print(validation)
```

### Test MCP Orchestrator
```python
from mcp_orchestrator import process_mcp_request

result = process_mcp_request("Get Account 001Xx000010SQA")
print(result)
```

### Test Session Manager
```python
from session_manager import SessionManager

sm = SessionManager()
session_id = sm.create_session("Test Session")
sm.add_user_message("Test message")
print(sm.list_sessions())
```

## 📚 Documentation

- **[CHAT_INTERFACE.md](CHAT_INTERFACE.md)** - Complete chat interface guide
- **[TOOLS_DOCUMENTATION.md](TOOLS_DOCUMENTATION.md)** - Detailed tool API reference
- **[QUICKSTART.md](QUICKSTART.md)** - Quick reference guide
- **[examples.py](examples.py)** - Code examples and demos

## 🔧 Advanced Usage

### Programmatic Tool Usage
```python
from tools import TOOLS

# Direct tool invocation
account = TOOLS['get_record']('Account', '001Xx000010SQA')
TOOLS['update_record']('Account', '001Xx000010SQA', {'Phone': '+1-555-0100'})
summary = TOOLS['summarize_record']('Account', '001Xx000010SQA')
validation = TOOLS['validate_update']('Account', '001Xx000010SQA', {'Phone': '+1-555-0100'})
```

### Custom Session Management
```python
from session_manager import SessionManager

sm = SessionManager()
sm.create_session("Important Session")
sm.add_user_message("User query")
sm.add_assistant_message("Assistant response")
exported = sm.export_session(session_id, "markdown")
print(exported)
```

### Tool Orchestration
```python
from mcp_orchestrator import get_orchestrator

orchestrator = get_orchestrator()
result = orchestrator.process_request(
    "Update Account 001Xx000010SQA phone",
    enable_validation=True
)
summary = orchestrator.get_execution_summary()
```

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| ModuleNotFoundError | Run `pip install -r requirements.txt` |
| Salesforce connection fails | Verify `.env` credentials and security token |
| Sessions not saving | Check `.sessions` directory permissions |
| Tools not found | Verify TOOLS dictionary in tools.py |
| LangGraph errors | Ensure Python 3.8+ and typing-extensions installed |

## 📈 Performance Tips

1. **Use field selection** in get_record for large objects
2. **Enable validation mode** for production operations
3. **Export sessions** regularly for backup
4. **Monitor execution history** via sidebar stats
5. **Batch operations** using tool chaining

## 🤝 Contributing

To extend functionality:

1. **Add new tools**: Create function in `tools.py`, add to TOOLS registry
2. **Custom workflows**: Extend `MCPOrchestrator` in `mcp_orchestrator.py`
3. **UI enhancements**: Modify `chat_app.py` using Streamlit APIs
4. **Session features**: Extend `SessionManager` in `session_manager.py`

## 📝 License

MIT License - Feel free to use and modify

## 🆘 Support

For issues or questions:
1. Check the Help section in the chat app sidebar
2. Review documentation files (CHAT_INTERFACE.md, TOOLS_DOCUMENTATION.md)
3. Check examples.py for code samples
4. Verify .env configuration

## 🎯 Roadmap

- [ ] Multi-user support
- [ ] Custom tool creation UI
- [ ] Advanced analytics dashboard
- [ ] Scheduled operations
- [ ] Webhook integrations
- [ ] Custom LLM integration
- [ ] Team collaboration features

## 🚀 Next Steps

1. **Run the app**: `streamlit run chat_app.py`
2. **Try examples**: Use sample queries in the Help section
3. **Export chats**: Backup important conversations
4. **Customize**: Adjust settings to your needs
5. **Share**: Collaborate with your team

---

**Built with ❤️ for Salesforce automation**

For the latest features and updates, check the [CHAT_INTERFACE.md](CHAT_INTERFACE.md) guide.
