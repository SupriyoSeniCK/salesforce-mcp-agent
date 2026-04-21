# chat_app.py
"""
Professional chat interface for Salesforce MCP Agent.
Features:
- Session persistence
- Conversation history
- Tool orchestration
- Real-time interactions
- Export capabilities
"""

import streamlit as st
from session_manager import SessionManager
from agent import handle_query_with_validation, handle_query, list_mcp_tools
from tools import TOOLS


# Page configuration
st.set_page_config(
    page_title="Salesforce MCP Chat Agent",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session manager
if "session_manager" not in st.session_state:
    st.session_manager = SessionManager()
    # Create initial session
    session_id = st.session_manager.create_session("New Chat")
    st.session_state.current_session_id = session_id
else:
    st.session_manager = st.session_state.get("session_manager")
    if "current_session_id" not in st.session_state:
        session_id = st.session_manager.create_session("New Chat")
        st.session_state.current_session_id = session_id


def render_sidebar():
    """Render the sidebar with session management"""
    with st.sidebar:
        st.markdown("## 📋 Conversation Manager")
        
        # Current session info
        current_session = st.session_manager.get_current_session()
        if current_session:
            with st.container(border=True):
                st.markdown(f"**Current Session:**")
                st.markdown(f"🆔 `{current_session.session_id[:12]}...`")
                st.markdown(f"📝 **{current_session.title}**")
                st.markdown(f"💬 Messages: **{current_session.metadata['message_count']}**")
                st.markdown(f"🔧 Tools Used: **{current_session.metadata.get('tool_calls', 0)}**")
        
        st.divider()
        
        # New conversation button
        col1, col2 = st.columns(2)
        with col1:
            if st.button("➕ New Chat", use_container_width=True):
                session_id = st.session_manager.create_session("New Chat")
                st.session_state.current_session_id = session_id
                st.rerun()
        
        with col2:
            if st.button("🗑️ Clear", use_container_width=True):
                if current_session:
                    st.session_manager.reset_session()
                st.rerun()
        
        st.divider()
        
        # Session history
        st.markdown("### 📚 History")
        sessions = st.session_manager.list_sessions()
        
        if sessions:
            for session in sessions[:10]:  # Show last 10 sessions
                session_id = session["session_id"]
                is_current = session_id == st.session_state.current_session_id
                
                # Display session with click option
                container = st.container(border=is_current)
                with container:
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        if st.button(
                            f"📌 {session['title']}\n`{session['message_count']}` messages",
                            use_container_width=True,
                            key=f"session_{session_id}"
                        ):
                            st.session_manager.load_session(session_id)
                            st.session_state.current_session_id = session_id
                            st.rerun()
                    
                    with col2:
                        if st.button("×", key=f"delete_{session_id}", help="Delete"):
                            st.session_manager.delete_session(session_id)
                            st.rerun()
        else:
            st.info("No previous conversations")
        
        st.divider()
        
        # Export options
        st.markdown("### ⬇️ Export")
        export_format = st.selectbox("Format:", ["JSON", "Markdown", "Text"])
        
        if st.button("📥 Export Current Chat", use_container_width=True):
            if current_session:
                format_map = {"JSON": "json", "Markdown": "markdown", "Text": "txt"}
                exported = st.session_manager.export_session(
                    current_session.session_id,
                    format_map[export_format]
                )
                if exported:
                    st.download_button(
                        label=f"Download as {export_format}",
                        data=exported,
                        file_name=f"chat_{current_session.session_id}.{format_map[export_format]}",
                        mime="text/plain"
                    )
        
        st.divider()
        
        # Settings
        with st.expander("⚙️ Settings"):
            query_mode = st.radio(
                "Query Mode:",
                ["Standard", "With Validation"],
                help="Standard: Direct processing. With Validation: Extra safety checks"
            )
            st.session_state.query_mode = query_mode
            
            st.markdown("**Available Tools:**")
            for tool_name in TOOLS.keys():
                st.markdown(f"- 🔧 `{tool_name}`")
        
        st.divider()
        
        # Help
        with st.expander("❓ Help"):
            st.markdown("""
            **How to use:**
            1. Type your request about Salesforce
            2. Agent will choose appropriate tools
            3. View results and history
            
            **Example queries:**
            - Get the Account 001Xx000010SQA
            - Update Contact 003Xx000004TMA phone
            - Summarize Opportunity 006Xx000001SVPA
            
            **Tools:**
            - `get_record`: Fetch records
            - `update_record`: Modify records
            - `summarize_record`: Quick summary
            - `validate_update`: Check before update
            """)


def process_user_message(user_input: str) -> None:
    """Send a message through the agent and persist both sides of the exchange."""
    current_session = st.session_manager.get_current_session()
    session_id = current_session.session_id if current_session else ""
    conversation_context = st.session_manager.get_context_for_llm(session_id=session_id, max_messages=8)
    st.session_manager.add_user_message(user_input)

    with st.spinner("Processing your request..."):
        try:
            query_mode = st.session_state.get("query_mode", "Standard")

            if query_mode == "With Validation":
                response_data = handle_query_with_validation(
                    user_input,
                    conversation_context=conversation_context,
                    session_id=session_id,
                )
                response = response_data.get("response", "No response")
                tool_info = {
                    "mode": "validation",
                    "validation": response_data.get("validation"),
                    "session_id": response_data.get("session_id"),
                    "tool_info": response_data.get("tool_info"),
                }
            else:
                response_data = handle_query(
                    user_input,
                    conversation_context=conversation_context,
                    session_id=session_id,
                )
                response = response_data.get("response", "No response")
                tool_info = {
                    "mode": "standard",
                    "session_id": response_data.get("session_id"),
                    "decision": response_data.get("decision"),
                    "tool_info": response_data.get("tool_info"),
                }

            st.session_manager.add_assistant_message(response, tool_info)
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            st.session_manager.add_assistant_message(error_msg)


def render_chat_interface():
    """Render the main chat interface"""
    st.markdown("# Salesforce MCP Chat Agent")
    st.caption("Chat with the agent about Salesforce records. Conversations are saved automatically.")

    current_session = st.session_manager.get_current_session()
    history = current_session.messages if current_session else []
    session_id = current_session.session_id if current_session else "not-initialized"

    info_col1, info_col2 = st.columns([3, 2])
    with info_col1:
        st.markdown(f"**Session ID:** `{session_id}`")
    with info_col2:
        st.markdown(f"**Turns:** `{len(history)}`")

    if not history:
        with st.chat_message("assistant"):
            st.markdown(
                "Ask me about a Salesforce record, update, or summary. "
                "Follow-up questions in this same session will use recent chat context."
            )

    for msg in history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and msg.get("tool_info"):
                with st.expander("Tool Details"):
                    st.json(msg["tool_info"])

    prompt = st.chat_input("Ask about a Salesforce record or update...")
    if prompt:
        process_user_message(prompt)
        st.rerun()

    st.divider()
    st.markdown("### Quick Actions")

    col1, col2, col3, col4 = st.columns(4)

    if col1.button("Get Sample", use_container_width=True):
        process_user_message("Get the Account record 001Xx000010SQA")
        st.rerun()

    if col2.button("Summarize Sample", use_container_width=True):
        process_user_message("Summarize the Contact 003Xx000004TMA")
        st.rerun()

    if col3.button("List Tools", use_container_width=True):
        tool_listing = list_mcp_tools(session_id)
        with st.chat_message("assistant"):
            st.markdown("Available MCP tools for this session:")
            st.json(tool_listing.get("result", {}).get("tools", []))

    if col4.button("Show Stats", use_container_width=True):
        current = st.session_manager.get_current_session()
        if current:
            st.info(
                f"Messages: {current.metadata['message_count']} | "
                f"Tools used: {current.metadata.get('tool_calls', 0)}"
            )


def main():
    """Main application"""
    render_sidebar()
    render_chat_interface()


if __name__ == "__main__":
    main()
