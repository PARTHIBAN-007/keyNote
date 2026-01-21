from fastapi import FastAPI
from contextlib import asynccontextmanager
from loguru import logger
from fastapi.middleware.cors import CORSMiddleware
from src.config import get_settings
from src.db.factory import make_database
from src.routers import ping, events, ask


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting RAG API...")

    settings = get_settings()
    app.state.settings = settings

    database = make_database()
    app.state.database = database
    logger.info("Database connected")

    yield  

    logger.info("Shutting down RAG API...")


app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods=["*"], 
    allow_headers = ["*"],

)

@app.get("/")
async def get_status():
    return "Hello World"


app.include_router(ping.router)
app.include_router(ask.router)
app.include_router(events.router)
