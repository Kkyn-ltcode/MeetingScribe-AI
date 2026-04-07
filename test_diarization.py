from services.api_gateway.app.diarizer import Diarizer
import os

diarizer = Diarizer(hf_token=os.getenv("HF_TOKEN"))
segments = diarizer.diarize("bnw.wav")

for seg in segments:
    print(f"{seg['speaker']}: {seg['start']}s - {seg['end']}s")
