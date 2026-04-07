import logging
import redis.asyncio as aioredis
from contextlib import asynccontextmanager
from fastapi import FastAPI
from .config import config
from .db import engine 
from .models import Base
from .routers.meetings import router as meetings_router
from .websockets import router as ws_router
from .transcriber import Transcriber

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting API Gateway connected to {config.POSTGRES_HOST}...")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created successfully")

    app.state.redis = aioredis.from_url(config.REDIS_URL, decode_responses=True)
    logger.info("Redis connected")

    app.state.transcriber = Transcriber(model_size='tiny')
    logger.info("Transcriber ready")

    yield

    await app.state.redis.aclose()
    logger.info("Redis disconnected")
    logger.info('Shutting down API Gateway...')

app = FastAPI(title='MeetingScribe AI', lifespan=lifespan)
app.include_router(meetings_router, prefix="/api")
app.include_router(ws_router)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "meeting-scribe-api"
    }