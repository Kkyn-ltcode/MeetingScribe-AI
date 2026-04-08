from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from .db import AsyncSessionLocal
from .models import LiveTranscript, Participant
from sqlalchemy import select
import logging
import uuid

logger = logging.getLogger(__name__)
router = APIRouter()

@router.websocket("/ws/transcribe/{meeting_id}/{participant_id}")
async def transcribe_stream(websocket: WebSocket, meeting_id: str, participant_id: str):
    await websocket.accept()
    transcriber = websocket.app.state.transcriber
    async with AsyncSessionLocal() as session:
        query = select(Participant).where(
            Participant.id == participant_id
        )
        participant = await session.execute(query)
        participant = participant.scalar_one_or_none()
        display_name = participant.display_name if participant else "Unknown"
        logger.info(f"{display_name} connected to meeting {meeting_id}")

    try:
        while True:
            audio_chunk = await websocket.receive_bytes()

            result = transcriber.add_chunk(audio_chunk)
            if result:
                text, detected_language = result
                if text and text != "[silence]":
                    async with AsyncSessionLocal() as session:
                        transcript = LiveTranscript(
                            meeting_id=meeting_id,
                            participant_id=participant_id,
                            text=text,
                            language=detected_language
                        )
                        session.add(transcript)
                        await session.commit()
                    await websocket.send_text(text)
                elif text == "[silence]":
                    await websocket.send_text("[silence]")
                else:
                    await websocket.send_text("[buffering...]")
    except WebSocketDisconnect:
        result = transcriber.flush()
        if result:
            text, detected_language = result
            if text and text != "[silence]":
                async with AsyncSessionLocal() as session:
                    transcript = LiveTranscript(
                        meeting_id=meeting_id,
                        text=text
                    )
                    session.add(transcript)
                    await session.commit()
                await websocket.send_text(text)
            logger.info(f"Meeting {meeting_id} ended")