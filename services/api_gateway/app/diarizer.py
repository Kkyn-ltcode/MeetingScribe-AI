from pyannote.audio import Pipeline
import logging

logger = logging.getLogger(__name__)

class Diarizer:
    def __init__(self, hf_token: str):
        logger.info("Loading Diarization model...")
        self.pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token=hf_token
        )
        logger.info("Diarization model loaded!")

    def diarize(self, audio_path: str) -> list[dict]:
        diarization = self.pipeline(audio_path)

        segments = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            segments.append({
                "speaker": speaker,
                'start': round(turn.start, 2),
                "end": round(turn.end, 2)
            })
        return segments