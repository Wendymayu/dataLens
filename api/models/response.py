"""Pydantic response models for API"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ChatResponse(BaseModel):
    """Chat response"""
    response: str
    sql: Optional[str] = None
    conversation_id: str
    message_id: str
    created_at: datetime
    duration: Optional[float] = None  # 耗时（秒）


class DatabaseResponse(BaseModel):
    """Database info response"""
    name: str
    host: str
    port: int
    user: str
    database: str
    is_current: bool
    connection_status: Optional[str] = None


class ConfigResponse(BaseModel):
    """Config response (masked sensitive data)"""
    provider: str
    model_name: str
    api_key_masked: str
    base_url: Optional[str]
    temperature: float
    max_tokens: int
    current_database: Optional[str]


class MessageResponse(BaseModel):
    """Single message in conversation"""
    id: str
    role: str
    content: str
    sql: Optional[str] = None
    created_at: datetime


class ConversationResponse(BaseModel):
    """Conversation with messages"""
    id: str
    title: str
    database: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse]


class ConversationListItem(BaseModel):
    """Conversation list item"""
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int


class ProviderInfo(BaseModel):
    """Provider information"""
    id: str
    name: str
    description: str
    default_model: str
    supports_base_url: bool