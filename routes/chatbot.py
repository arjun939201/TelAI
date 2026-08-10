"""
routes/chatbot.py

/api/chat endpoint.

Frontend contract:

POST /api/chat

Request:
{
    "message": "...",
    "history": [...]
}

Response:
{
    "reply": "..."
}
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.grok_chat import (
    generate_reply,
    GroqRequestError,
)


router = APIRouter()


# ============================================================
# CHAT MESSAGE
# ============================================================

class ChatMessage(BaseModel):

    role: str
    content: str


# ============================================================
# CHAT REQUEST
# ============================================================

class ChatRequest(BaseModel):

    message: str
    history: Optional[List[ChatMessage]] = None


# ============================================================
# CHAT RESPONSE
# ============================================================

class ChatResponse(BaseModel):

    reply: str


# ============================================================
# CHAT ENDPOINT
# ============================================================

@router.post(
    "/chat",
    response_model=ChatResponse
)
async def chat(
    request: ChatRequest
):

    message = request.message.strip()

    if not message:

        raise HTTPException(
            status_code=400,
            detail="message cannot be empty."
        )


    history_dicts = []

    if request.history:

        for msg in request.history:

            history_dicts.append(
                {
                    "role": msg.role,
                    "content": msg.content
                }
            )


    try:

        reply = generate_reply(
            message,
            history_dicts
        )

    except GroqRequestError as exc:

        print(
            "GROQ ERROR:",
            exc.status_code,
            exc.message
        )

        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.message
        )

    except Exception as exc:

        print(
            "CHAT ERROR:",
            repr(exc)
        )

        raise HTTPException(
            status_code=500,
            detail="Chat service failed."
        )


    return ChatResponse(
        reply=reply
    )
