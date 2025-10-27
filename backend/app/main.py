"""
OrcheNet Backend - FastAPI Application
Main entry point for the API server.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
from .routers import devices, tasks, checkin

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="OrcheNet API",
    description="Network device orchestration and management platform",
    version="0.1.0"
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

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "OrcheNet API",
        "version": "0.1.0",
        "status": "running"
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}
