from typing import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from socialAPI.main import app
from socialAPI.router.post import comment_table, post_table


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture()
def client() -> Generator:
    yield TestClient(app)

@pytest.fixture()
async def db() -> AsyncGenerator:
    post_table.clear()
    comment_table.clear()
    yield client