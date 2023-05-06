from typing import Any
from datetime import datetime, date
from pydantic import BaseModel, validator, ValidationError
import uuid

class UserBaseSchema(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    birthday: date | None = None
    biography: str | None = None
    city: str | None = None

class UserCreateSchema(UserBaseSchema):
    password: str 

class UserUpdateSchema(UserBaseSchema):
    password: str | None = None
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

class UserPublicSchema(UserBaseSchema):
    id: uuid.UUID
    age: int

class UserSchema(UserBaseSchema):
    id: uuid.UUID | None = None
    created_at: datetime | None = None
    edited_at: datetime | None = None
    deleted: bool | None = None
    password_salt: str | None = None
    password_hash: str | None = None
