from typing import Dict, Any, Optional
from fastapi import APIRouter
from pydantic import BaseModel
from app.core.config import settings

router = APIRouter()


class SettingsUpdate(BaseModel):
    llm_provider: Optional[str] = None
    openai_api_key: Optional[str] = None
    openai_base_url: Optional[str] = None
    openai_model: Optional[str] = None
    ollama_base_url: Optional[str] = None
    ollama_model: Optional[str] = None
    default_browser: Optional[str] = None
    headless: Optional[bool] = None
    confidence_threshold: Optional[float] = None


@router.get("")
def get_current_settings():
    return {
        "llm_provider": settings.LLM_PROVIDER,
        "openai_configured": bool(settings.OPENAI_API_KEY),
        "openai_base_url": settings.OPENAI_BASE_URL,
        "openai_model": settings.OPENAI_MODEL,
        "ollama_base_url": settings.OLLAMA_BASE_URL,
        "ollama_model": settings.OLLAMA_MODEL,
        "default_browser": settings.DEFAULT_BROWSER,
        "headless": settings.HEADLESS,
        "confidence_threshold": settings.CONFIDENCE_THRESHOLD,
        "max_retries": settings.MAX_RETRIES
    }


@router.post("")
def update_settings(data: SettingsUpdate):
    if data.llm_provider is not None:
        settings.LLM_PROVIDER = data.llm_provider
    if data.openai_api_key is not None:
        settings.OPENAI_API_KEY = data.openai_api_key
    if data.openai_base_url is not None:
        settings.OPENAI_BASE_URL = data.openai_base_url
    if data.openai_model is not None:
        settings.OPENAI_MODEL = data.openai_model
    if data.ollama_base_url is not None:
        settings.OLLAMA_BASE_URL = data.ollama_base_url
    if data.ollama_model is not None:
        settings.OLLAMA_MODEL = data.ollama_model
    if data.default_browser is not None:
        settings.DEFAULT_BROWSER = data.default_browser
    if data.headless is not None:
        settings.HEADLESS = data.headless
    if data.confidence_threshold is not None:
        settings.CONFIDENCE_THRESHOLD = data.confidence_threshold

    return {"status": "SUCCESS", "settings": get_current_settings()}
