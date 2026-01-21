"""
FastAPI Application - Main Entry Point

LEARNING NOTES:
---------------
FastAPI serves your bot as an HTTP API with:
- Automatic Swagger documentation at /docs
- Request/response validation
- Async support

KEY CONCEPTS:
-------------
1. LIFESPAN: Initialize bot on startup, cleanup on shutdown
2. ROUTERS: Organize endpoints into modules
3. CORS: Allow cross-origin requests from browsers

YOUR TASK: (See roadmap.md Step 8)
----------
This file is mostly complete. Just ensure your graph works first!
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from portfolio_bot.configs.app_config import get_config
from portfolio_bot.api.routes.chat import router as chat_router
from portfolio_bot.logs.logger import setup_logging, get_logger
from portfolio_bot.core.graph import PortfolioBot


setup_logging()
logger = get_logger(__name__)


# Global bot instance, initialized in lifespan
bot: PortfolioBot | None = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Initialize bot on startup, cleanup on shutdown."""
    logger.info("Starting Portfolio Bot API...")

    global bot
    bot = PortfolioBot()
    await bot.initialize()
    app.state.bot = bot

    yield

    logger.info("Shutting down...")


app = FastAPI(
    title="Portfolio Bot API",
    description="A LangGraph-powered chatbot",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api", tags=["chat"])

# Serve the UI (simple static SPA)
_STATIC_DIR = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "portfolio-bot"}


@app.get("/")
async def root():
    return {"message": "Portfolio Bot API", "docs": "/docs"}


@app.get("/chat")
async def chat_ui():
    """Serve the chat UI."""
    return FileResponse(_STATIC_DIR / "index.html")


