from fastapi import APIRouter
from pydantic import BaseModel

from services.grok_chat import chat_with_grok


router = APIRouter(
    prefix="/api"
)


class ChatRequest(BaseModel):

    message: str
    history: list = []


@router.post("/chat")
async def chat(request: ChatRequest):

    if not request.message.strip():

        return {
            "reply": ""
        }


    reply = chat_with_grok(
        request.message,
        request.history
    )


    return {
        "reply": reply
    }
