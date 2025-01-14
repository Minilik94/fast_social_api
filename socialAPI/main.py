import logging
from asgi_correlation_id import CorrelationIdMiddleware
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.exception_handlers import http_exception_handler


from socialAPI.database import database
from socialAPI.logging_conf import configure_logging
from socialAPI.router.post import router as post_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()

    await database.connect()
    yield
    await database.disconnect()


app = FastAPI(lifespan=lifespan)
app.add_middleware(CorrelationIdMiddleware)

app.include_router(post_router, prefix="/api/v1/posts")


@app.exception_handler(HTTPException)
async def http_exception_handler_logging(request, exc):
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return await http_exception_handler(request, exc)
