"""Chat API router"""
from fastapi import APIRouter, HTTPException
from api.models.request import ChatRequest
from api.models.response import ChatResponse
from api.services.agent_service import AgentService
from api.services.conversation_service import ConversationService
from datetime import datetime
import time

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a query and get response"""
    agent_service = AgentService.get_instance()
    conv_service = ConversationService()

    # Check if database is configured
    current_db = request.database or agent_service.config_manager.config.current_database
    if not current_db:
        raise HTTPException(400, "No database configured. Please add a database first.")

    # Create or get conversation
    if request.conversation_id:
        conv = conv_service.get_conversation(request.conversation_id)
        if not conv:
            raise HTTPException(404, "Conversation not found")
    else:
        conv = conv_service.create_conversation(database=current_db)

    # Add user message
    conv_service.add_message(conv.id, "user", request.query)

    # Get response from agent
    try:
        start_time = time.time()
        # Pass session_id to agent service for memory continuity
        response = await agent_service.query(
            request.query,
            request.database,
            session_id=request.session_id or conv.id  # Use session_id or conversation_id
        )
        sql = agent_service.extract_sql(response)
        duration = time.time() - start_time

        # Add assistant message
        message = conv_service.add_message(conv.id, "assistant", response, sql)

        return ChatResponse(
            response=response,
            sql=sql,
            conversation_id=conv.id,
            message_id=message.id,
            created_at=message.created_at,
            duration=duration
        )
    except Exception as e:
        raise HTTPException(500, str(e))