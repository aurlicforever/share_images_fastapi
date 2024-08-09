import asyncio
import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database.database import engine, SessionLocal, Base
from sqlalchemy.orm import Session
from typing import List, Annotated
from routers import user_router
from routers import auth_router
from routers import country_router
from routers import category_router
from routers import post_router
from routers import comment_router
from routers import like_post_router
from routers import token_router
from models import category, country, comment, like_post, post, app_user

from core.api_key_header_middleware import get_api_key

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(app_user.Base.metadata.create_all)
        await conn.run_sync(category.Base.metadata.create_all)
        await conn.run_sync(country.Base.metadata.create_all)
        await conn.run_sync(comment.Base.metadata.create_all)
        await conn.run_sync(like_post.Base.metadata.create_all)
        await conn.run_sync(post.Base.metadata.create_all)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
    
db_dependency = Annotated[Session, Depends(get_db)]

origins = [
    "http://localhost:4200",
]

def include_router(app):
    app.include_router(auth_router.router, dependencies=[Depends(get_api_key)])
    app.include_router(country_router.router, dependencies=[Depends(get_api_key)])
    app.include_router(comment_router.router, dependencies=[Depends(get_api_key)])
    app.include_router(category_router.router, dependencies=[Depends(get_api_key)])
    app.include_router(like_post_router.router, dependencies=[Depends(get_api_key)])
    app.include_router(token_router.router, dependencies=[Depends(get_api_key)])
    app.include_router(user_router.router, dependencies=[Depends(get_api_key)])
    app.include_router(post_router.router, dependencies=[Depends(get_api_key)])

def start_application():
    app = FastAPI(title="Share images API",version="1.0.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    include_router(app)
    static_files_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
    app.mount("/assets", StaticFiles(directory=static_files_path), name="post")
    return app

app = start_application()

@app.on_event("startup")
async def on_startup():
    await create_tables()

@app.get("/")
def read_root():
    return {"Share Images": "1.0.0"}