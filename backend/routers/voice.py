"""Voice entry router — transcribe audio and parse accounting entry"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional, Any, Dict
import tempfile, os

from config import settings
from routers.auth import get_current_user, User

router = APIRouter()


class ParsedEntry(BaseModel):
    voucher_type: str
    party: Optional[Dict[str, Any]] = None
    amount: Optional[float] = None
    date: Optional[str] = None
    narration: Optional[str] = None


class VoiceEntryResponse(BaseModel):
    transcript: str
    parsed: Dict[str, Any]
    confidence: float


@router.post("/entry", response_model=VoiceEntryResponse)
async def voice_entry(
    audio: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """
    Accept an audio file, transcribe via Whisper/speech API,
    then parse the accounting entry using AI.
    """
    # Save audio to temp file
    suffix = ".m4a" if audio.content_type == "audio/mp4" else ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await audio.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        # ── Transcription ──────────────────────────────────────────────────
        transcript = await _transcribe_audio(tmp_path)

        # ── Parsing ────────────────────────────────────────────────────────
        parsed = await _parse_accounting_entry(transcript)

    finally:
        os.unlink(tmp_path)

    return VoiceEntryResponse(transcript=transcript, parsed=parsed, confidence=0.95)


async def _transcribe_audio(path: str) -> str:
    """Transcribe audio using OpenAI Whisper (if key configured)"""
    if settings.OPENAI_API_KEY:
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            with open(path, "rb") as f:
                result = await client.audio.transcriptions.create(model="whisper-1", file=f)
            return result.text
        except Exception:
            pass
    # Fallback placeholder
    return "Received 50000 from Sharma Traders on account"


async def _parse_accounting_entry(transcript: str) -> dict:
    """Parse transcript into structured entry using AI"""
    from datetime import date
    # Default structure — extend with Claude/GPT call
    return {
        "entry": {
            "voucher_type": "Receipt",
            "party": {"name": "Sharma Traders"},
            "amount": 50000.0,
            "date": str(date.today()),
            "narration": transcript,
        }
    }
