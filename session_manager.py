# session_manager.py
"""
Session manager for persisting and managing chat conversations.
Handles session storage, retrieval, and restoration.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path


class ConversationSession:
    """Represents a single conversation session"""
    
    def __init__(self, session_id: str, title: str = "New Conversation"):
        self.session_id = session_id
        self.title = title
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        self.messages: List[Dict[str, Any]] = []
        self.metadata: Dict[str, Any] = {
            "status": "active",
            "message_count": 0,
            "tool_calls": 0
        }
    
    def add_message(self, role: str, content: str, tool_info: Optional[Dict] = None):
        """Add a message to the conversation"""
        message = {
            "role": role,  # "user" or "assistant"
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "tool_info": tool_info
        }
        self.messages.append(message)
        self.updated_at = datetime.now().isoformat()
        self.metadata["message_count"] = len(self.messages)
        
        if tool_info:
            self.metadata["tool_calls"] = self.metadata.get("tool_calls", 0) + 1
    
    def to_dict(self) -> Dict:
        """Convert session to dictionary"""
        return {
            "session_id": self.session_id,
            "title": self.title,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "messages": self.messages,
            "metadata": self.metadata
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'ConversationSession':
        """Create session from dictionary"""
        session = ConversationSession(data["session_id"], data.get("title", "Restored Conversation"))
        session.created_at = data.get("created_at", datetime.now().isoformat())
        session.updated_at = data.get("updated_at", datetime.now().isoformat())
        session.messages = data.get("messages", [])
        session.metadata = data.get("metadata", {})
        return session
    
    def get_summary(self) -> str:
        """Get a summary of the conversation"""
        return f"{self.title} ({self.metadata['message_count']} messages, {self.metadata.get('tool_calls', 0)} tool calls)"


class SessionManager:
    """Manages conversation sessions and persistence"""
    
    def __init__(self, storage_dir: str = ".sessions"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        self.sessions: Dict[str, ConversationSession] = {}
        self.current_session: Optional[ConversationSession] = None
    
    def create_session(self, title: str = "New Conversation") -> str:
        """Create a new conversation session"""
        session_id = self._generate_session_id()
        session = ConversationSession(session_id, title)
        self.sessions[session_id] = session
        self.current_session = session
        self._save_session(session)
        return session_id
    
    def load_session(self, session_id: str) -> Optional[ConversationSession]:
        """Load a specific session"""
        if session_id in self.sessions:
            self.current_session = self.sessions[session_id]
            return self.sessions[session_id]
        
        # Try to load from disk
        session_data = self._load_session_from_disk(session_id)
        if session_data:
            session = ConversationSession.from_dict(session_data)
            self.sessions[session_id] = session
            self.current_session = session
            return session
        
        return None
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all available sessions"""
        sessions_info = []
        
        for session_id, session in self.sessions.items():
            sessions_info.append({
                "session_id": session_id,
                "title": session.title,
                "created_at": session.created_at,
                "updated_at": session.updated_at,
                "message_count": session.metadata["message_count"]
            })
        
        # Also load sessions from disk that aren't in memory
        if self.storage_dir.exists():
            for session_file in self.storage_dir.glob("*.json"):
                session_id = session_file.stem
                if session_id not in self.sessions:
                    data = self._load_session_from_disk(session_id)
                    if data:
                        sessions_info.append({
                            "session_id": session_id,
                            "title": data.get("title", "Unknown"),
                            "created_at": data.get("created_at", "Unknown"),
                            "updated_at": data.get("updated_at", "Unknown"),
                            "message_count": len(data.get("messages", []))
                        })
        
        return sorted(sessions_info, key=lambda x: x["updated_at"], reverse=True)
    
    def get_current_session(self) -> Optional[ConversationSession]:
        """Get the current active session"""
        return self.current_session
    
    def add_user_message(self, content: str) -> None:
        """Add a user message to current session"""
        if not self.current_session:
            self.create_session()
        self.current_session.add_message("user", content)
        self._save_session(self.current_session)
    
    def add_assistant_message(self, content: str, tool_info: Optional[Dict] = None) -> None:
        """Add an assistant message to current session"""
        if not self.current_session:
            self.create_session()
        self.current_session.add_message("assistant", content, tool_info)
        self._save_session(self.current_session)
    
    def get_conversation_history(self, session_id: Optional[str] = None) -> List[Dict]:
        """Get conversation history for a session"""
        session = self.sessions.get(session_id)
        if not session and session_id:
            session = self.load_session(session_id)
        if not session:
            session = self.current_session
        
        if not session:
            return []
        
        return session.messages
    
    def get_context_for_llm(self, session_id: Optional[str] = None, max_messages: int = 10) -> str:
        """Get formatted context for LLM from conversation history"""
        history = self.get_conversation_history(session_id)
        
        # Get last N messages
        recent_messages = history[-max_messages:] if len(history) > max_messages else history
        
        context = "Conversation History:\n\n"
        for msg in recent_messages:
            role = msg["role"].upper()
            content = msg["content"]
            context += f"{role}: {content}\n"
        
        return context
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            if self.current_session and self.current_session.session_id == session_id:
                self.current_session = None
        
        session_file = self.storage_dir / f"{session_id}.json"
        if session_file.exists():
            session_file.unlink()
            return True
        
        return False
    
    def export_session(self, session_id: str, output_format: str = "json") -> Optional[str]:
        """Export a session to file or string"""
        session = self.sessions.get(session_id)
        if not session:
            session = self.load_session(session_id)
        
        if not session:
            return None
        
        if output_format == "json":
            return json.dumps(session.to_dict(), indent=2)
        elif output_format == "markdown":
            return self._to_markdown(session)
        elif output_format == "txt":
            return self._to_text(session)
        
        return None
    
    def _save_session(self, session: ConversationSession) -> None:
        """Save session to disk"""
        session_file = self.storage_dir / f"{session.session_id}.json"
        with open(session_file, 'w') as f:
            json.dump(session.to_dict(), f, indent=2)
    
    def _load_session_from_disk(self, session_id: str) -> Optional[Dict]:
        """Load session from disk"""
        session_file = self.storage_dir / f"{session_id}.json"
        if session_file.exists():
            with open(session_file, 'r') as f:
                return json.load(f)
        return None
    
    def _generate_session_id(self) -> str:
        """Generate a unique session ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        counter = len(self.sessions) + 1
        return f"session_{timestamp}_{counter}"
    
    def _to_markdown(self, session: ConversationSession) -> str:
        """Convert session to markdown format"""
        md = f"# {session.title}\n\n"
        md += f"**Created:** {session.created_at}\n"
        md += f"**Updated:** {session.updated_at}\n"
        md += f"**Messages:** {session.metadata['message_count']}\n\n"
        md += "---\n\n"
        
        for msg in session.messages:
            role = "👤 User" if msg["role"] == "user" else "🤖 Assistant"
            md += f"### {role}\n"
            md += f"{msg['content']}\n\n"
            if msg.get("tool_info"):
                md += f"*Tool: {msg['tool_info'].get('tool', 'Unknown')}*\n\n"
        
        return md
    
    def _to_text(self, session: ConversationSession) -> str:
        """Convert session to plain text format"""
        text = f"{session.title}\n"
        text += f"{'='*60}\n"
        text += f"Created: {session.created_at}\n"
        text += f"Updated: {session.updated_at}\n\n"
        
        for msg in session.messages:
            role = "USER" if msg["role"] == "user" else "ASSISTANT"
            text += f"[{role}] {msg['content']}\n"
            if msg.get("tool_info"):
                text += f"  (Tool: {msg['tool_info'].get('tool')})\n"
            text += "\n"
        
        return text
    
    def reset_session(self) -> None:
        """Reset/clear current session"""
        if self.current_session:
            self.current_session.messages = []
            self.current_session.metadata["message_count"] = 0
            self.current_session.metadata["tool_calls"] = 0
            self._save_session(self.current_session)
