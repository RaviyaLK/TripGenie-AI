# schemas.py
from pydantic import BaseModel, Field
from typing import List


class ChatPart(BaseModel):
    text: str

class ChatMessage(BaseModel):
    role: str
    parts: List[ChatPart]

class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = Field(default_factory=list)

class ChatResponse(BaseModel):
    role: str
    parts: List[ChatPart]


class ExtractedInfo(BaseModel):
    intent: str = Field(description="The user's goal, e.g., 'search_hotels', 'find_attractions', 'general_chat'.")
    city: str | None = Field(description="The city name mentioned by the user, if any.")
    parameters: dict = Field(default_factory=dict, description="Other relevant parameters.")