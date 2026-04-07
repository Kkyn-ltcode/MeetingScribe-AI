import asyncio
import wave
import struct
import math
import websockets

def generate_test_wave(filename="test_audio.wav", duration=2, sample_rate=16000):
    n_samples = duration * sample_rate

    with wave.open(filename, "w") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)

        for i in range(n_samples):
            sample = int(32767 * math.sin(2 * math.pi * 440 * i / sample_rate))
            wav.writeframes(struct.pack("<h", sample))
    print(f"Genarated {filename} ({duration}s, {sample_rate}Hz)")
    return filename

async def send_audio(meeting_id: str):
    filename = "bnw.wav"

    with open(filename, "rb") as f:
        audio_bytes = f.read()

    print(f"Audio file size: {len(audio_bytes)} bytes")

    chunk_size = 32000

    async with websockets.connect(f"ws://localhost:8000/ws/transcribe/{meeting_id}") as ws:
        for i in range(0, len(audio_bytes), chunk_size):
            chunk = audio_bytes[i:i + chunk_size]
            await ws.send(chunk)
            response = await ws.recv()
            print(f"Chunk {i//chunk_size + 1}: {response}")
        print("All audio sent!")

asyncio.run(send_audio("d0ff2505-0715-450a-962c-9c7c2076538c"))