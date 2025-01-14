import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from socialAPI.router.post import router as post_router
from socialAPI.database import database
from socialAPI.logging_conf import configure_logging

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    logger.info("Starting the application")
    logger.info("Connecting to the database")
    logger.info("Connected to the database")
    logger.info("Stopping the application")
    logger
    await database.connect()
    yield
    await database.disconnect()


app = FastAPI(lifespan=lifespan)


app.include_router(post_router, prefix="/api/v1/posts")
