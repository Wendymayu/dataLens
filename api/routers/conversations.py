"""Conversation history API router"""
from fastapi import APIRouter, HTTPException
from api.models.request import ConversationCreateRequest, ConversationTitleUpdateRequest
from api.models.response import ConversationResponse, ConversationListItem, MessageResponse
from api.services.conversation_service import ConversationService
from datetime import datetime
from typing import List

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


@router.get("", response_model=List[ConversationListItem])
async def list_conversations():
    """List all conversations"""
    conv_service = ConversationService()
    return conv_service.list_conversations()


@router.post("", response_model=ConversationResponse)
async def create_conversation(request: ConversationCreateRequest = None):
    """Create new conversation"""
    conv_service = ConversationService()
    title = request.title if request else None
    conv = conv_service.create_conversation(title=title)

    return ConversationResponse(
        id=conv.id,
        title=conv.title,
        database=conv.database,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        messages=[]
    )


@router.get("/{conv_id}", response_model=ConversationResponse)
async def get_conversation(conv_id: str):
    """Get conversation with messages"""
    conv_service = ConversationService()
    conv = conv_service.get_conversation(conv_id)

    if not conv:
        raise HTTPException(404, "Conversation not found")

    messages = [
        MessageResponse(
            id=msg.id,
            role=msg.role,
            content=msg.content,
            sql=msg.sql,
            created_at=msg.created_at
        )
        for msg in conv.messages
    ]

    return ConversationResponse(
        id=conv.id,
        title=conv.title,
        database=conv.database,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        messages=messages
    )


@router.patch("/{conv_id}/title")
async def update_conversation_title(conv_id: str, request: ConversationTitleUpdateRequest):
    """Update conversation title"""
    conv_service = ConversationService()

    if not conv_service.update_title(conv_id, request.title):
        raise HTTPException(404, "Conversation not found")

    return {"status": "success", "title": request.title}


@router.delete("/{conv_id}")
async def delete_conversation(conv_id: str):
    """Delete conversation"""
    conv_service = ConversationService()

    if not conv_service.delete_conversation(conv_id):
        raise HTTPException(404, "Conversation not found")

    return {"status": "success"}