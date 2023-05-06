from typing import Any
from datetime import datetime, date
from pydantic import BaseModel, validator, ValidationError
import uuid

class LoginSchema(BaseModel):
    user_id: str
    password: str