from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel, EmailStr, field_serializer, field_validator


class EmailSchema(BaseModel):
    email: EmailStr
    captchaToken: str

class VerifyOTP(BaseModel):
    email: EmailStr
    code: str

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tag: Optional[str] = None
    color: Optional[str] = None

class TagResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class NoteShortResponse(BaseModel):
    id: int
    userId: int
    title: str
    color: str
    updated_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    @field_serializer('updated_at', 'created_at')
    def serialize_dt(self, dt: datetime, _info):
        if dt is None:
            return None
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt

class NoteResponse(BaseModel):
    id: int
    userId: int
    title: str
    content: str
    color: str
    tags: List[TagResponse]

    updated_at: datetime
    created_at: datetime

    @field_serializer('updated_at', 'created_at')
    def serialize_dt(self, dt: datetime, _info):
        # Если из SQLite пришло время без зоны, мы помечаем его как UTC
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt

class UserTagResponse(BaseModel):
    id: int
    name: str
    note_ids: List[int] = []

    @field_validator("note_ids", mode="before")
    @classmethod
    def extract_note_ids(cls, v, info):
        if isinstance(v, list) and len(v) > 0 and hasattr(v[0], 'id'):
            return [note.id for note in v]
        return v

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    email: str
    password: str
    captchaToken: Optional[str] = None

class UserSettingsSchema(BaseModel):
    note_display: int
    note_sort: int
    tags_sort: bool
    theme: int

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: int
    email: str

    settings: UserSettingsSchema

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: str
    password: str
    captchaToken: str

class TokenConfirmSchema(BaseModel):
    token: str