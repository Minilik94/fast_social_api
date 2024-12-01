from fastapi import APIRouter, HTTPException

from socialAPI.models.posts import UserPost, UserPostIn, Comment, CommentIn, UserPostWithComments

router = APIRouter()


post_table = {}
comment_table = {}


@router.post("/", response_model=UserPost, status_code=201)
async def create_post(post: UserPostIn):
    data = post.model_dump()
    last_post_id = len(post_table)

    new_post = {**data, "id": last_post_id}
    post_table[last_post_id] = new_post
    return new_post


@router.get("/", response_model=list[UserPost])
async def get_all_posts():
    return list(post_table.values())


def find_post(post_id: int):
    if post_id in post_table:
        return post_table[post_id]


@router.post("/comment", response_model=Comment, status_code=201)
async def create_comment(comment: CommentIn):
    post = find_post(comment.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    data = comment.model_dump()
    last_comment_id = len(comment_table)

    new_comment = {**data, "id": last_comment_id}
    comment_table[last_comment_id] = new_comment
    return new_comment


@router.get("/comment", response_model=list[Comment])
async def get_all_comments():
    return list(comment_table.values())


@router.get("/{post_id}/comment", response_model=list[Comment])
async def get_comments_on_post(post_id: int):
    return [
        comment for comment in comment_table.values() if comment["post_id"] == post_id
    ]


@router.get('/{post_id}', response_model=UserPostWithComments)
async def get_post_with_comments(post_id: int):
    post = find_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return {
        "post": post,
        "comments": await get_comments_on_post(post_id)
    }