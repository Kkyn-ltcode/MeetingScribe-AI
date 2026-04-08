import uuid
import random
import string
from datetime import datetime
from sqlalchemy import String, DateTime, func, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

def generate_room_code() -> str:
    chars = string.ascii_uppercase + string.digits
    part1 = ''.join(random.choices(chars, k=3))
    part2 = ''.join(random.choices(chars, k=3))
    return f"{part1}-{part2}"

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

class Meeting(Base):
    __tablename__ = "meetings"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default='recording')
    room_code: Mapped[str] = mapped_column(String(7), unique=True, default=generate_room_code)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

class LiveTranscript(Base):
    __tablename__ = 'live_transcripts'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    meeting_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('meetings.id'), nullable=False)
    participant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('participants.id'), nullable=True)
    language: Mapped[str]= mapped_column(String(10), default='en')
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

class Participant(Base):
    __tablename__ = 'participants'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    meeting_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('meetings.id'), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    language: Mapped[str] = mapped_column(String(10), nullable=False, default='en')
    joined_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())