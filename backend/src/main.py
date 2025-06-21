from fastapi import FastAPI
import os
from contextlib import asynccontextmanager
from api.db import initdb
from api.chat.routing import router as chat_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    #before app startup
    initdb()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(chat_router, prefix = '/api/chats')
API_KEY = os.environ.get("API_KEY")
if not API_KEY:
    raise NotImplementedError(" API_KEY environment variable is not set. Please set it before running the application.")
@app.get("/")
def read_index():
    return {"message": "Welcome to the FastAPI application! This is the index page."}   