"""TaxMind AI router — chat with AI assistant about accounting/tax queries"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Any, Dict, List

from config import settings
from routers.auth import get_current_user, User

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None
    history: Optional[List[Dict[str, str]]] = None


class ChatResponse(BaseModel):
    reply: str
    sources: List[str] = []
    model_used: str


@router.post("/chat", response_model=ChatResponse)
async def chat(
    body: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    """Chat with TaxMind AI — answers GST, TDS, accounting questions"""
    reply, model = await _get_ai_response(body.message, body.context, body.history)
    return ChatResponse(reply=reply, model_used=model)


async def _get_ai_response(
    message: str,
    context: Optional[Dict] = None,
    history: Optional[List] = None,
) -> tuple[str, str]:
    system_prompt = (
        "You are TaxMind AI, an expert accounting assistant for Indian CA firms. "
        "You help with GST, TDS, income tax, accounting entries, and reconciliation. "
        "Always cite relevant sections of Indian tax law when applicable."
    )

    if settings.ANTHROPIC_API_KEY:
        try:
            import anthropic
            client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
            messages = (history or []) + [{"role": "user", "content": message}]
            response = await client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                system=system_prompt,
                messages=messages,
            )
            return response.content[0].text, "claude-3-5-sonnet"
        except Exception:
            pass

    if settings.OPENAI_API_KEY:
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            messages_list = [{"role": "system", "content": system_prompt}]
            messages_list += (history or [])
            messages_list.append({"role": "user", "content": message})
            response = await client.chat.completions.create(
                model="gpt-4o-mini", messages=messages_list, max_tokens=1024
            )
            return response.choices[0].message.content, "gpt-4o-mini"
        except Exception:
            pass

    # Fallback
    return (
        "I'm TaxMind AI. Please configure an AI API key (Anthropic or OpenAI) to enable full AI responses.",
        "fallback",
    )
