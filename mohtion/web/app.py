"""FastAPI application factory."""

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from mohtion.config import get_settings
from mohtion.web.routes import health, webhooks

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler."""
    settings = get_settings()
    logging.basicConfig(level=settings.log_level)
    logger.info("Mohtion starting up...")
    yield
    logger.info("Mohtion shutting down...")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="Mohtion",
        description="Autonomous Tech Debt Bounty Hunter",
        version="0.1.0",
        debug=settings.debug,
        lifespan=lifespan,
    )

    # Register routes
    app.include_router(health.router, tags=["health"])
    app.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])

    # Mount static files for landing page (must be LAST, acts as catch-all)
    static_dir = Path(__file__).parent.parent.parent / "static"
    logger.info(f"[STATIC] Looking for static directory at: {static_dir}")
    logger.info(f"[STATIC] Absolute path: {static_dir.absolute()}")
    logger.info(f"[STATIC] Directory exists: {static_dir.exists()}")

    if static_dir.exists():
        try:
            contents = list(static_dir.iterdir())
            logger.info(f"[STATIC] Directory contains {len(contents)} items")
            logger.info(f"[STATIC] Contents: {[item.name for item in contents[:10]]}")  # First 10 items
            logger.info(f"[STATIC] Mounting static files at / with html=True")
            app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
            logger.info(f"[STATIC] Successfully mounted static files")
        except Exception as e:
            logger.error(f"[STATIC] Error mounting static files: {e}")
    else:
        logger.warning(f"[STATIC] Static directory NOT FOUND at {static_dir}")
        logger.warning(f"[STATIC] Landing page will not be available")

    return app


# Default app instance for uvicorn
app = create_app()
