from datetime import datetime

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: str | None
    owner_id: int
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }
