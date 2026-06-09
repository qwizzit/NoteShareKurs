from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table, DateTime, func, Boolean
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import BOOLEANTYPE

from .database import Base

note_tags = Table(
    "note_tags",
    Base.metadata,
    Column("note_id", Integer, ForeignKey("notes.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True)
)
note_collaborators = Table(
    "note_collaborators",
    Base.metadata,
    Column("note_id", Integer, ForeignKey("notes.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
)

class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    userId = Column(Integer, ForeignKey("users.id"))
    title = Column(String, default="New note")
    content = Column(Text, default="")
    color = Column(String, default="#B2BEB5")

    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    tags = relationship("Tag", secondary=note_tags, back_populates="notes")

    collaborators = relationship("User", secondary=note_collaborators, backref="shared_notes")

    def __repr__(self):
        return f"<Note {self.id}>"


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    notes = relationship("Note", secondary=note_tags, back_populates="tags")

    def __repr__(self):
        return f"<Tag {self.name}>"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=False, nullable=False)
    password = Column(String)

    settings = Column(JSON, default={
        "note_display": 1,
        "note_sort": 1,
        "tags_sort": False,
        "theme": 1
    })

    otp_code = Column(String, nullable=True)
    otp_expires_at = Column(DateTime, nullable=True)