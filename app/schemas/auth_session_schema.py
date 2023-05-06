from typing import Any
from datetime import datetime, date
from pydantic import BaseModel, validator, ValidationError
import uuid

class AuthSessionUpdateSchema(BaseModel):
    expires_at: datetime | None = None

class AuthSessionCreateSchema(AuthSessionUpdateSchema):
    user_id: uuid.UUID
    token: str

class AuthSessionPublicSchema(AuthSessionCreateSchema):
    id: uuid.UUID | None = None
    created_at: datetime | None = None
    edited_at: datetime | None = None

class AuthSessionSchema(AuthSessionPublicSchema):
    deleted: bool | None = None
