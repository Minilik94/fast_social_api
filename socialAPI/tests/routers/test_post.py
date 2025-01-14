import pytest
from httpx import AsyncClient


# Utility functions
async def create_post(body: str, async_client: AsyncClient) -> dict:
    response = await async_client.post("/api/v1/posts/", json={"body": body})
    response.raise_for_status()  # Ensure an exception is raised on HTTP errors
    return response.json()


async def create_comment(body: str, post_id: int, async_client: AsyncClient) -> dict:
    response = await async_client.post(
        "/api/v1/comments/", json={"body": body, "post_id": post_id}
    )
    response.raise_for_status()
    return response.json()


# Fixtures
@pytest.fixture
async def created_post(async_client: AsyncClient):
    return await create_post("Test post", async_client)


@pytest.fixture
async def created_comment(async_client: AsyncClient, created_post: dict):
    return await create_comment("Test comment", created_post["id"], async_client)


# Tests
@pytest.mark.anyio
async def test_get_all_posts(async_client: AsyncClient):
    body = "test post"

    # Create a post
    response = await async_client.post("/api/v1/posts/", json={"body": body})

    assert response.status_code == 201
    post_data = response.json()

    # Assertions
    assert post_data["body"] == body
    assert "id" in post_data
    assert isinstance(post_data["id"], int)

    # Validate retrieval of posts
    get_response = await async_client.get("/api/v1/posts/")
    assert get_response.status_code == 200
    all_posts = get_response.json()

    assert any(post["body"] == body for post in all_posts)


@pytest.mark.anyio
async def test_create_comment(async_client: AsyncClient, created_post: dict):
    body = "test comment"

    # Create a comment for the post
    response = await async_client.post(
        "/api/v1/posts/{post_id}/comment", json={"body": body, "post_id": }
    )
    assert response.status_code == 201

    comment_data = response.json()

    # Assertions
    assert comment_data["body"] == body
    assert comment_data["post_id"] == created_post["id"]
    assert "id" in comment_data

    # Validate retrieval of comments
    get_response = await async_client.get(
        f"/api/v1/posts/{created_post['id']}/comments/"
    )
    assert get_response.status_code == 200
    comments = get_response.json()

    assert any(comment["body"] == body for comment in comments)
