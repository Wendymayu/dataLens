"""Pydantic request models for API"""
from pydantic import BaseModel, Field
from typing import Optional


class ChatRequest(BaseModel):
    """Chat query request"""
    query: str = Field(..., description="Natural language query")
    conversation_id: Optional[str] = Field(None, description="Conversation ID")
    database: Optional[str] = Field(None, description="Database name to use")


class DatabaseCreateRequest(BaseModel):
    """Create database request"""
    name: str = Field(..., description="Database connection name")
    host: str = Field("localhost", description="Database host")
    port: int = Field(3306, description="Database port")
    user: str = Field(..., description="Database user")
    password: str = Field(..., description="Database password")
    database: str = Field(..., description="Database name")


class ModelConfigRequest(BaseModel):
    """Update model config request"""
    provider: str = Field(..., description="Model provider")
    model_name: str = Field(..., description="Model name")
    api_key: str = Field(..., description="API key")
    base_url: Optional[str] = Field(None, description="Base URL for OpenAI-compatible")
    temperature: float = Field(0.7, ge=0.0, le=1.0, description="Temperature")
    max_tokens: int = Field(4096, description="Max tokens")


class ConversationCreateRequest(BaseModel):
    """Create conversation request"""
    title: Optional[str] = Field(None, description="Conversation title")


class ConversationTitleUpdateRequest(BaseModel):
    """Update conversation title"""
    title: str = Field(..., description="New title")