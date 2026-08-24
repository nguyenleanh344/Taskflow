from datetime import datetime

from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    status: str = Field(default="pending", max_length=30)


class TaskUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )
    description: str | None = None
    status: str | None = Field(
        default=None,
        max_length=30,
    )


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None
    status: str
    project_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }
