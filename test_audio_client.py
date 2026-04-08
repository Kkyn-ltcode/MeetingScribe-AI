import asyncio
import wave
import struct
import math
import websockets

meeting_id = "664f1f6b-88d6-4d62-be49-15bfbad88c38"
participant_id = "89809a27-7830-4277-8d77-d904125ddff8"

async def send_audio(meeting_id: str, participant_id: str):
    filename = "bnw.wav"

    with open(filename, "rb") as f:
        audio_bytes = f.read()

    print(f"Audio file size: {len(audio_bytes)} bytes")

    chunk_size = 32000

    async with websockets.connect(f"ws://localhost:8000/ws/transcribe/{meeting_id}/{participant_id}") as ws:
        for i in range(0, len(audio_bytes), chunk_size):
            chunk = audio_bytes[i:i + chunk_size]
            await ws.send(chunk)
            response = await ws.recv()
            print(f"Chunk {i//chunk_size + 1}: {response}")
        print("All audio sent!")

asyncio.run(send_audio(meeting_id, participant_id))