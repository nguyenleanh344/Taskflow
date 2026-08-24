from datetime import datetime

from pydantic import BaseModel, Field


class CommentCreate(BaseModel):
    content: str = Field(min_length=1)


class CommentUpdate(BaseModel):
    content: str = Field(min_length=1)


class CommentResponse(BaseModel):
    id: int
    content: str
    task_id: int
    author_id: int
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }