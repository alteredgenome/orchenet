"""
OrcheNet Backend - FastAPI Application
Main entry point for the API server.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
from .routers import devices, tasks, checkin, wireguard, webcli, provision
from .services.task_processor import task_processor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info("Starting OrcheNet API server...")

    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified")

    # Start task processor
    await task_processor.start()
    logger.info("Task processor started")

    yield

    # Shutdown
    logger.info("Shutting down OrcheNet API server...")
    await task_processor.stop()
    logger.info("Task processor stopped")


app = FastAPI(
    title="OrcheNet API",
    description="Network device orchestration and management platform",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(devices.router)
app.include_router(tasks.router)
app.include_router(checkin.router)
app.include_router(wireguard.router)
app.include_router(webcli.router)
app.include_router(provision.router)

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "OrcheNet API",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "task_processor": "running" if task_processor.running else "stopped"
    }
