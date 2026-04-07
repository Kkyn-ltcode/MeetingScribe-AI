# 📓 MeetingScribe AI — Learning Journal

> This document tracks the full engineering journey of building MeetingScribe AI from scratch, guided by a Senior Architect mentorship approach.

---

## Session 1 — 2026-04-05

### What I Built Today
Starting from zero knowledge of Docker, I built a complete real-time audio transcription system in one session:

```
Phone/Client
    │
    ├── POST /api/meetings          → Creates a meeting in PostgreSQL
    │
    ├── WS /ws/transcribe/{id}      → Streams live audio bytes
    │       │
    │       ├── Whisper AI Model     → Converts audio → text
    │       └── Returns live text    → Back to the client
    │
    └── GET /api/meetings/{id}/transcripts  → Read saved notes
```

### Files Created
| File | Purpose |
|---|---|
| `docker-compose.yaml` | Runs PostgreSQL + Redis locally via Docker containers |
| `.env` | Stores database credentials securely (never committed to Git) |
| `.gitignore` | Prevents secrets, venvs, and large files from being pushed |
| `services/api-gateway/app/config.py` | 12-Factor config using Pydantic BaseSettings |
| `services/api-gateway/app/main.py` | FastAPI app with async lifespan (singleton pattern) |
| `services/api-gateway/app/db.py` | Async SQLAlchemy engine + session factory |
| `services/api-gateway/app/models.py` | User, Meeting, LiveTranscript database models |
| `services/api-gateway/app/routers/meetings.py` | REST endpoints for meeting CRUD |
| `services/api-gateway/app/websockets.py` | WebSocket endpoint for live audio streaming |
| `services/api-gateway/app/transcriber.py` | Whisper model wrapper for speech-to-text |
| `test_audio_client.py` | Test client that streams audio over WebSocket |

### Key Concepts Learned

#### 1. Docker & Docker Compose
- Containers are isolated mini-computers running inside your computer
- `docker-compose.yaml` is a recipe that starts multiple services (Postgres, Redis) together
- Volumes persist data even when containers are destroyed
- YAML syntax requires strict indentation and spacing

#### 2. Environment Variables & 12-Factor Apps
- Never hardcode passwords in source code
- Store secrets in `.env` files (excluded from Git via `.gitignore`)
- Use `pydantic-settings` to validate and centralize all configuration

#### 3. FastAPI Lifespan Pattern
- Senior engineers initialize database connections ONCE at startup (singleton)
- The `@asynccontextmanager` lifespan replaces the deprecated `@app.on_event`
- Code before `yield` = startup; code after `yield` = shutdown

#### 4. SQLAlchemy ORM
- Models are Python classes that map to database tables
- Foreign Keys enforce referential integrity (can't create a meeting for a non-existent user)
- `flush()` sends SQL to DB but doesn't save permanently; `commit()` does
- `echo=True` prints every SQL query for debugging

#### 5. WebSockets
- HTTP = sending letters (request → response → done)
- WebSockets = phone call (persistent, two-way, real-time)
- `receive_text()` for text data, `receive_bytes()` for binary data
- Path parameters like `/{meeting_id}` let you route different meetings

#### 6. Audio Processing & ML Inference
- Digital audio: 16kHz sample rate × 16-bit = 32,000 bytes per second
- `faster-whisper` uses CTranslate2 for optimized inference on CPU
- The `tiny` model (39MB) is fast but less accurate; `small` (461MB) is better
- Chunking audio at rigid byte boundaries cuts words in half — overlapping windows fix this

#### 7. Silent Bugs vs. Loud Bugs
- **Loud bugs** (SyntaxError) crash immediately — easy to find
- **Silent bugs** (misspelled keyword argument like `nnullable`) run fine but produce wrong behavior — much more dangerous
- This is why unit tests exist

### Debugging Wins
1. Fixed YAML syntax errors (missing spaces after dashes, misspelled `volumes`)
2. Fixed Pydantic `.env` file path (relative path `../../.env` vs `../../../.env`)
3. Fixed Foreign Key violation by creating real user before meeting
4. Fixed WebSocket 405 error by understanding GET vs POST methods
5. Understood why Whisper stutters on chunk boundaries ("T-T-T-today's")

### Architecture Decisions Made
| Decision | Chosen | Why |
|---|---|---|
| Config library | `pydantic-settings` | Strict typing + automatic `.env` loading |
| Database driver | `asyncpg` | Non-blocking I/O for high concurrency |
| ORM | SQLAlchemy 2.0 (async) | Industry standard, Alembic migrations |
| Task queue | `arq` (planned) | Native asyncio, lighter than Celery |
| Speech model | `faster-whisper` (tiny) | Fast CPU inference for development |

---

## Next Session Goals
- [ ] Save transcribed text back to the database (combine WebSocket + DB)
- [ ] Implement overlapping audio buffer (fix word-slicing)
- [ ] Speaker Diarization (know WHO said what)
- [ ] Git branching and pull request workflow
