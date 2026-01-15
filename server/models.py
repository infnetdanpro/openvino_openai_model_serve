from typing import List, Optional

from pydantic import BaseModel, Field


class Message(BaseModel):
    role: str = Field(
        ...,
        description="Role of the message sender, e.g., 'user' or 'assistant'",
        example="user",
    )
    content: str = Field(
        ..., description="Content of the message", example="Hello, how are you?"
    )


class ChatRequest(BaseModel):
    model: str
    messages: List[Message]
    stream: Optional[bool] = False
    temperature: Optional[float] = 1.0
