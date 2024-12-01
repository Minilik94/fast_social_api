from fastapi import FastAPI
from socialAPI.router.post import router as post_router

app = FastAPI()


app.include_router(post_router, prefix="/api/v1/posts")
