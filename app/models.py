
from typing import Dict, List, Literal
from pydantic import BaseModel, Field


class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=8000)
    mode: Literal["standard", "melimi"] = "standard"
    history: List[ChatTurn] = Field(default_factory=list)


class WordRegistration(BaseModel):
    word: str
    melimi_equivalent: str
    root: str = ""
    meaning: str = ""
    part_of_speech: str = ""
    formation: str = ""


class ChatResponse(BaseModel):
    reply: str
    mode: str
    intent: str
    understanding: Dict = Field(default_factory=dict)
    language_audit: Dict = Field(default_factory=dict)
    word_audit: List[Dict] = Field(default_factory=list)


class LearningItem(BaseModel):
    kind: str
    standard: str = ""
    melimi: str = ""
    rule: str = ""
    meaning: str = ""
    evidence: str = ""
    source: str = "chat"
    status: Literal["pending", "approved", "rejected"] = "pending"
    confidence: float = 0.5


class LearningStatusUpdate(BaseModel):
    status: Literal["pending", "approved", "rejected"]


class HealthResponse(BaseModel):
    status: str
    service: str
    vocabulary_entries: int
