from fastapi import APIRouter
from pydantic import BaseModel

from services.grok_chat import chat_with_grok


router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    history: list = []


@router.post("/chat")
async def chat(request: ChatRequest):

    if not request.message.strip():
        return {
            "reply": "Please enter a message."
        }

   reply = chat_with_grok(
    request.message,
    request.history
)

reply = apply_melimi_replacements(reply)
    return {
        "reply": reply
    }
