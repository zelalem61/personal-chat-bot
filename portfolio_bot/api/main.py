"""
FastAPI Application - Main Entry Point

LEARNING NOTES:
---------------
This is the main FastAPI application that serves the portfolio bot as an API.

FastAPI is a modern Python web framework that provides:
- Automatic API documentation (Swagger UI)
- Request/response validation with Pydantic
- Async support out of the box
- High performance

KEY CONCEPTS:
-------------
1. LIFESPAN: Manages startup/shutdown events
   - Initialize resources on startup (bot, database connections)
   - Clean up on shutdown

2. DEPENDENCY INJECTION: FastAPI's Depends() system
   - Provides shared resources to route handlers
   - Handles resource lifecycle

3. ROUTERS: Organize routes into modules
   - Keep main.py clean
   - Group related endpoints

WHAT YOU'LL LEARN:
- FastAPI application structure
- Lifespan management for async resources
- Including routers
- CORS configuration
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from portfolio_bot.configs.app_config import get_config
from portfolio_bot.core.graph import PortfolioBot
from portfolio_bot.api.routes.chat import router as chat_router
from portfolio_bot.logs.logger import setup_logging, get_logger

# Initialize logging
setup_logging()
logger = get_logger(__name__)

# Global bot instance (initialized in lifespan)
bot: PortfolioBot = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Lifespan context manager for startup and shutdown events.

    This is the modern way to handle application lifecycle in FastAPI
    (replaces the deprecated @app.on_event decorators).

    LEARNING NOTE: The lifespan pattern ensures:
    1. Resources are initialized before handling requests
    2. Resources are properly cleaned up on shutdown
    3. Errors during startup prevent the app from starting

    The 'yield' separates startup (before) from shutdown (after).
    """
    global bot

    logger.info("Starting Portfolio Bot API...")

    # Startup: Initialize the bot
    try:
        bot = PortfolioBot()
        await bot.initialize()
        logger.info("Portfolio Bot initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize bot: {e}")
        raise

    # Make bot available to routes via app.state
    app.state.bot = bot

    yield  # Application runs here

    # Shutdown: Clean up resources
    logger.info("Shutting down Portfolio Bot API...")
    # Add cleanup code here if needed (close connections, etc.)


# Create the FastAPI application
app = FastAPI(
    title="Portfolio Bot API",
    description="A LangGraph-powered chatbot for portfolio assistance",
    version="0.1.0",
    lifespan=lifespan,
)


# Configure CORS (Cross-Origin Resource Sharing)
# This allows the API to be called from web browsers on different domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(chat_router, prefix="/api", tags=["chat"])


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint.

    Returns basic health status. Useful for:
    - Load balancer health checks
    - Kubernetes readiness probes
    - Monitoring systems
    """
    return {
        "status": "healthy",
        "service": "portfolio-bot",
        "version": "0.1.0",
    }


@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "message": "Welcome to the Portfolio Bot API",
        "docs": "/docs",
        "health": "/health",
        "chat": "/api/chat",
    }


# =============================================================================
# RUNNING THE APPLICATION
# =============================================================================

if __name__ == "__main__":
    """
    Run the application directly for development.

    For production, use:
        uvicorn portfolio_bot.api.main:app --host 0.0.0.0 --port 8004

    Or with auto-reload for development:
        uvicorn portfolio_bot.api.main:app --reload --port 8004
    """
    import uvicorn

    config = get_config()

    logger.info(f"Starting server on {config.api_host}:{config.api_port}")
    logger.info(f"Swagger docs available at http://localhost:{config.api_port}/docs")

    uvicorn.run(
        "portfolio_bot.api.main:app",
        host=config.api_host,
        port=config.api_port,
        reload=True,  # Enable auto-reload for development
    )
