import io
import wave
import numpy as np
from faster_whisper import WhisperModel
import logging

logger = logging.getLogger(__name__)

SAMPLE_RATE = 16000
BYTES_PER_SAMPLE = 2

class Transcriber:
    def __init__(self, model_size: str = 'base', buffer_seconds: float = 3.0):
        logger.info(f"Loading Whisper model: {model_size}...")

        self.model = WhisperModel(model_size, device="cpu", compute_type="int8")
        logger.info("Whisper model loaded!")

        self.buffer_seconds = buffer_seconds
        self.buffer_size = int(buffer_seconds * SAMPLE_RATE * BYTES_PER_SAMPLE)
        self.buffer = b""

    def add_chunk(self, audio_chunk: bytes) -> str | None:
        self.buffer += audio_chunk

        if len(self.buffer) > self.buffer_size:
            text, language = self._transcribe_bytes(self.buffer)
            self.buffer = b""
            return (text, language)
        else:
            return (None, None)

    def flush(self) -> str | None:
        if len(self.buffer) > BYTES_PER_SAMPLE * SAMPLE_RATE * 0.5:
            text, language = self._transcribe_bytes(self.buffer)
            self.buffer = b""
            return (text, language)
        self.buffer = b""
        return (None, None)
        
    def _transcribe_bytes(self, audio_bytes: bytes) -> str:
        audio_array = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0

        segments, info = self.model.transcribe(audio_array, beam_size=5)

        text = " ".join([segment.text.strip() for segment in segments])

        detected_language = info.language
        return (text if text else "[silence]", detected_language)