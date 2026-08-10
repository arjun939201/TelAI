from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.grok_chat import (
    generate_reply,
    GroqRequestError,
)


router = APIRouter()


class ChatMessage(BaseModel):

    role: str

    content: str


class ChatRequest(BaseModel):

    message: str = Field(
        ...,
        min_length=1,
        max_length=4000,
    )

    history: Optional[
        List[ChatMessage]
    ] = None


class ChatResponse(BaseModel):

    reply: str


@router.post(
    "/chat",
    response_model=ChatResponse,
)
async def chat(
    request: ChatRequest,
):

    message = request.message.strip()

    if not message:
        raise HTTPException(
            status_code=400,
            detail="message cannot be empty.",
        )

    history = []

    if request.history:

        for item in request.history:

            if item.role not in (
                "user",
                "assistant",
            ):
                continue

            history.append(
                {
                    "role": item.role,
                    "content": item.content,
                }
            )

    try:

        reply = generate_reply(
            message,
            history,
        )

    except GroqRequestError as exc:

        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.message,
        )

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Chat service failed.",
        )

    return ChatResponse(
        reply=reply,
    )
