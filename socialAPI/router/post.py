import logging

from fastapi import APIRouter, HTTPException

from socialAPI.database import comment_tabel, database, post_table
from socialAPI.models.posts import (
    Comment,
    CommentIn,
    UserPost,
    UserPostIn,
    UserPostWithComments,
)

router = APIRouter()

logger = logging.getLogger(__name__)


@router.post("/", response_model=UserPost, status_code=201)
async def create_post(post: UserPostIn):
    logger.info("Creating a post")

    data = post.model_dump()
    query = post_table.insert().values(data)
    logger.debug(query)
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}


@router.get("/", response_model=list[UserPost])
async def get_all_posts():
    logger.info("Getting all posts")
    query = post_table.select()
    logger.debug(query)
    return await database.fetch_all(query)


async def find_post(post_id: int):
    logger.info(f"Finding post with id {post_id}")

    query = post_table.select().where(post_table.c.id == post_id)
    return await database.fetch_one(query)


@router.post("/comment", response_model=Comment, status_code=201)
async def create_comment(comment: CommentIn):
    logger.info("Creating a comment")

    post = await find_post(comment.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    data = comment.model_dump()
    query = comment_tabel.insert().values(data)
    logger.debug(query)
    last_comment_id = await database.execute(query)

    return {**data, "id": last_comment_id}


@router.get("/comment", response_model=list[Comment])
async def get_all_comments():
    logger.info("Getting all comments")
    query = comment_tabel.select()
    logger.debug(query)
    return await database.fetch_all(query)


@router.get("/{post_id}/comment", response_model=list[Comment])
async def get_comments_on_post(post_id: int):
    logger.info("Getting comments on post ")

    query = comment_tabel.select().where(comment_tabel.c.post_id == post_id)
    logger.debug(query)
    return await database.fetch_all(query)


# @router.get("/comment")


@router.get("/{post_id}", response_model=UserPostWithComments)
async def get_post_with_comments(post_id: int):
    logger.info(f"Getting post with comments for post id {post_id}")

    post = await find_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return {"post": post, "comments": await get_comments_on_post(post_id)}
