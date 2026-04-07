from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from .db import AsyncSessionLocal
from .models import LiveTranscript
import logging
import uuid

logger = logging.getLogger(__name__)
router = APIRouter()

@router.websocket("/ws/transcribe/{meeting_id}")
async def transcribe_stream(websocket: WebSocket, meeting_id: str):
    await websocket.accept()
    transcriber = websocket.app.state.transcriber
    logger.info(f"Client connected for meeting {meeting_id}")

    try:
        while True:
            audio_chunk = await websocket.receive_bytes()

            text = transcriber.add_chunk(audio_chunk)

            if text and text != "[silence]":
                async with AsyncSessionLocal() as session:
                    transcript = LiveTranscript(
                        meeting_id=meeting_id,
                        text=text
                    )
                    session.add(transcript)
                    await session.commit()
                await websocket.send_text(text)
            elif text == "[silence]":
                await websocket.send_text("[silence]")
            else:
                await websocket.send_text("[buffering...]")
    except WebSocketDisconnect:
        text = transcriber.flush()
        if text and text != "[silence]":
            async with AsyncSessionLocal() as session:
                transcript = LiveTranscript(
                    meeting_id=meeting_id,
                    text=text
                )
                session.add(transcript)
                await session.commit()
        logger.info(f"Meeting {meeting_id} ended")