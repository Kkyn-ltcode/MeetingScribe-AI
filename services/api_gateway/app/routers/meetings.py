import uuid
from sqlalchemy import select
from fastapi import APIRouter
from ..db import AsyncSessionLocal
from ..models import Meeting, User, LiveTranscript, Participant

router = APIRouter()

@router.post("/meetings")
async def create_meeting():
    async with AsyncSessionLocal() as session:
        test_user = User(
            email=f"test_{uuid.uuid4().hex[:8]}@example.com",
            password_hash="not_a_real_hash"
        )
        session.add(test_user)
        await session.flush()

        meeting = Meeting(user_id=test_user.id)
        session.add(meeting)
        await session.commit()

        return {
            "id": str(meeting.id),
            "room_code": meeting.room_code,
            "status": meeting.status,
            "created_at": str(meeting.created_at)
        }

@router.get("/meetings/{meeting_id}/transcripts")
async def get_transcripts(meeting_id: str):
    async with AsyncSessionLocal() as session:
        query = select(LiveTranscript).where(
            LiveTranscript.meeting_id == meeting_id
        ).order_by(LiveTranscript.created_at)

        all_transcripts = await session.execute(query)
        all_transcripts = all_transcripts.scalars().all()

        return {
            'meeting_id': meeting_id,
            'transcripts': [t.text for t in all_transcripts]
        }

@router.post("/meetings/join")
async def join_meeting(room_code: str, display_name: str, language: str = 'en'):
    async with AsyncSessionLocal() as session:
        query = select(Meeting).where(
            Meeting.room_code == room_code,
        )
        meeting = await session.execute(query)
        meeting = meeting.scalar_one_or_none()
        
        participant = Participant(
            meeting_id=meeting.id,
            user_id=meeting.user_id,
            display_name=display_name,
            language=language
        )

        session.add(participant)
        await session.commit()

        return {
            "meeting_id": participant.meeting_id,
            "participant_id": participant.id
        }