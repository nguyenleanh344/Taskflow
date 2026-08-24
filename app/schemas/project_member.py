from datetime import datetime

from pydantic import BaseModel


class ProjectMemberResponse(BaseModel):
    id: int
    project_id: int
    user_id: int
    joined_at: datetime

    model_config = {
        "from_attributes": True,
    }