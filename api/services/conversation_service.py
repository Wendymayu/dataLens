"""Conversation history management service"""
import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

# 配置限制
MAX_MESSAGES_PER_CONVERSATION = 50  # 每个会话最多消息数
MAX_CONVERSATIONS = 100  # 最多保存会话数


class Message(BaseModel):
    """Single message"""
    id: str
    role: str  # "user" or "assistant"
    content: str
    sql: Optional[str] = None
    created_at: datetime


class Conversation(BaseModel):
    """Conversation with messages"""
    id: str
    title: str
    database: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    messages: List[Message] = []
    menu_type: str = "smart-query"  # smart-query, adhoc-query, alert


class ConversationService:
    """Manage conversation history"""

    def __init__(self, data_dir: str = "data/conversations"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def list_conversations(self) -> List[Dict]:
        """List all conversations"""
        conversations = []
        for file in self.data_dir.glob("*.json"):
            try:
                with open(file, encoding="utf-8") as f:
                    data = json.load(f)
                    conversations.append({
                        "id": data["id"],
                        "title": data["title"],
                        "created_at": data["created_at"],
                        "updated_at": data["updated_at"],
                        "message_count": len(data.get("messages", [])),
                        "menu_type": data.get("menu_type", "smart-query")  # 兼容旧数据
                    })
            except Exception:
                continue

        # Sort by updated_at descending
        return sorted(
            conversations,
            key=lambda x: x["updated_at"],
            reverse=True
        )

    def get_conversation(self, conv_id: str) -> Optional[Conversation]:
        """Get conversation by ID"""
        file = self.data_dir / f"{conv_id}.json"
        if file.exists():
            with open(file, encoding="utf-8") as f:
                data = json.load(f)
                return Conversation(**data)
        return None

    def create_conversation(
        self,
        title: Optional[str] = None,
        database: Optional[str] = None,
        menu_type: str = "smart-query"
    ) -> Conversation:
        """Create new conversation"""
        # Clean up old conversations if exceed limit
        self._cleanup_old_conversations()

        conv_id = str(uuid.uuid4())
        now = datetime.now()
        conv = Conversation(
            id=conv_id,
            title=title or f"New Chat {now.strftime('%Y-%m-%d %H:%M')}",
            database=database,
            created_at=now,
            updated_at=now,
            messages=[],
            menu_type=menu_type
        )
        self._save_conversation(conv)
        return conv

    def _cleanup_old_conversations(self):
        """Clean up old conversations when exceed limit"""
        conversations = self.list_conversations()
        if len(conversations) >= MAX_CONVERSATIONS:
            # Delete the oldest conversations
            to_delete = conversations[MAX_CONVERSATIONS - 1:]
            for conv in to_delete:
                self.delete_conversation(conv["id"])

    def add_message(
        self,
        conv_id: str,
        role: str,
        content: str,
        sql: Optional[str] = None
    ) -> Message:
        """Add message to conversation"""
        conv = self.get_conversation(conv_id)
        if not conv:
            raise ValueError(f"Conversation {conv_id} not found")

        message = Message(
            id=str(uuid.uuid4()),
            role=role,
            content=content,
            sql=sql,
            created_at=datetime.now()
        )
        conv.messages.append(message)
        conv.updated_at = datetime.now()

        # Auto-generate title from first user message
        if role == "user" and len(conv.messages) == 1:
            conv.title = content[:50] + ("..." if len(content) > 50 else "")

        # Limit messages per conversation
        if len(conv.messages) > MAX_MESSAGES_PER_CONVERSATION:
            # Keep the first message (for context) and recent messages
            conv.messages = [conv.messages[0]] + conv.messages[-(MAX_MESSAGES_PER_CONVERSATION - 1):]

        self._save_conversation(conv)
        return message

    def update_title(self, conv_id: str, title: str) -> bool:
        """Update conversation title"""
        conv = self.get_conversation(conv_id)
        if not conv:
            return False

        conv.title = title
        conv.updated_at = datetime.now()
        self._save_conversation(conv)
        return True

    def delete_conversation(self, conv_id: str) -> bool:
        """Delete conversation"""
        file = self.data_dir / f"{conv_id}.json"
        if file.exists():
            file.unlink()
            return True
        return False

    def _save_conversation(self, conv: Conversation):
        """Save conversation to file"""
        file = self.data_dir / f"{conv.id}.json"
        with open(file, "w", encoding="utf-8") as f:
            json.dump(conv.model_dump(), f, default=str, indent=2)