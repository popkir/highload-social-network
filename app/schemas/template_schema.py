from typing import Any
from datetime import datetime
from pydantic import BaseModel, validator, ValidationError
import uuid

class TemplateCreateSchema(BaseModel):
    name: str  | None = None
    description: str | None = None
    count: int  | None = None
    price: float | None = None

class TemplateUpdateSchema(TemplateCreateSchema):
    deleted: Any | None = None

    @validator('deleted')
    def validate_deleted(cls, v):
        if v in [True, 'true', 'True', 'TRUE', 1, "1"]:
            return True
        elif v in [False, 'false', 'False', 'FALSE', 0, "0"]:
            return False
        elif v is None:
            return None
        else:
            raise ValidationError('"deleted", if present, must be a boolean')

class TemplateSchema(TemplateUpdateSchema):
    id: uuid.UUID | None = None
    created_at: datetime | None = None
    edited_at: datetime | None = None