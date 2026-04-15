"""Configuration API router"""
from fastapi import APIRouter, HTTPException
from api.models.request import ModelConfigRequest
from api.models.response import ConfigResponse, ProviderInfo
from api.services.agent_service import AgentService
from typing import List

router = APIRouter(prefix="/api/config", tags=["config"])


def mask_api_key(api_key: str) -> str:
    """Mask API key for safe display"""
    if len(api_key) <= 8:
        return "***"
    return api_key[:4] + "***" + api_key[-4:]


@router.get("", response_model=ConfigResponse)
async def get_config():
    """Get current configuration"""
    agent_service = AgentService.get_instance()
    config = agent_service.config_manager.config
    model = config.model

    return ConfigResponse(
        provider=model.provider,
        model_name=model.model_name,
        api_key_masked=mask_api_key(model.api_key),
        base_url=model.base_url,
        temperature=model.temperature,
        max_tokens=model.max_tokens,
        current_database=config.current_database
    )


@router.put("/model")
async def update_model_config(request: ModelConfigRequest):
    """Update model configuration"""
    agent_service = AgentService.get_instance()

    agent_service.config_manager.update_model(
        provider=request.provider,
        model_name=request.model_name,
        api_key=request.api_key,
        base_url=request.base_url
    )

    # Clear agent cache to use new model
    agent_service.clear_cache()

    return {
        "status": "success",
        "provider": request.provider,
        "model_name": request.model_name
    }


@router.get("/providers", response_model=List[ProviderInfo])
async def list_providers():
    """List supported model providers"""
    return [
        ProviderInfo(
            id="anthropic",
            name="Anthropic Claude",
            description="Claude models with tool use support",
            default_model="claude-3-5-sonnet-20241022",
            supports_base_url=False
        ),
        ProviderInfo(
            id="qwen",
            name="Alibaba Tongyi Qwen",
            description="Qwen models via DashScope",
            default_model="qwen-turbo",
            supports_base_url=False
        ),
        ProviderInfo(
            id="zhipu",
            name="Zhipu AI GLM",
            description="GLM models",
            default_model="glm-4",
            supports_base_url=False
        ),
        ProviderInfo(
            id="openai-compatible",
            name="OpenAI Compatible",
            description="OpenAI-compatible API (custom base URL)",
            default_model="",
            supports_base_url=True
        )
    ]