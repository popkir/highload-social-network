from sqlalchemy import Column, String, Float, Integer, DateTime, \
    Date, Boolean,  UUID, Text
from sqlalchemy.sql import func
import uuid

from app.db.db import Base

class TemplateModel(Base):
    __tablename__ = "template"

    # Technical fields not to be modified by user
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    edited_at = Column(DateTime(timezone=True), onupdate=func.now(), default=func.now())
    
    # Flag to mark as deleted
    deleted = Column(Boolean, default=False)
    
    # User fields
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    count = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)

    def __str__(self):
        return f"Template(id={self.id}, name={self.name}, description={self.description}, count={self.count}, price={self.price}, created_at={self.created_at}, edited_at={self.edited_at}, deleted={self.deleted})"
    
    def __repr__(self):
        return self.__str__()

class UserModel(Base):
    __tablename__ = "user"

    # Technical fields not to be modified by user
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    edited_at = Column(DateTime(timezone=True), onupdate=func.now(), default=func.now())

    # Authentication fields
    password_salt = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)

    # Flag to mark as deleted
    deleted = Column(Boolean, default=False)

    # User fields
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    birthday = Column(Date, nullable=False)
    biography = Column(Text, nullable=False)
    city = Column(String(255), nullable=False)

    def __str__(self):
        return f"User(id={self.id}, first_name={self.first_name}, last_name={self.last_name}, age={self.age}, biography={self.biography}, city={self.city},  created_at={self.created_at}, edited_at={self.edited_at}, deleted={self.deleted})"
    
    def __repr__(self):
        return self.__str__() 