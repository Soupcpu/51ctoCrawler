"""Main application"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time

from core.config import settings
from core.logging_config import setup_logging
from core.cache import init_cache, get_news_cache
from core.scheduler import get_scheduler, start_scheduler, stop_scheduler
from api import news_router

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="51CTO Backend API - HongYiXun Format",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )
    
    return response

# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Register routes
app.include_router(news_router)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "51CTO Backend API",
        "version": settings.app_version,
        "docs": "/docs",
        "redoc": "/redoc",
        "source": "51CTO",
        "format": "HongYiXun Compatible"
    }

# Health check
@app.get("/health")
async def health_check():
    try:
        cache = get_news_cache()
        cache_status = cache.get_status()
        
        return {
            "status": "healthy" if cache_status["status"] != "error" else "degraded",
            "timestamp": time.time(),
            "version": settings.app_version,
            "cache_status": cache_status["status"],
            "cache_count": cache_status["cache_count"]
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": time.time(),
            "version": settings.app_version,
            "error": str(e)
        }

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("Application starting...")
    
    # Initialize cache
    try:
        init_cache()
        logger.info("Cache initialized")
    except Exception as e:
        logger.error(f"Cache initialization failed: {e}")
        raise
    
    # Start scheduler
    try:
        start_scheduler()
        logger.info("Scheduler started")
    except Exception as e:
        logger.error(f"Scheduler start failed: {e}")
    
    # Execute initial cache load (auto crawl on startup)
    try:
        logger.info("Starting initial cache load...")
        scheduler = get_scheduler()
        await scheduler.initial_cache_load()
        logger.info("Initial cache load started in background")
    except Exception as e:
        logger.error(f"Initial cache load failed: {e}")
        # Don't raise, let server continue
    
    logger.info("Application started successfully")
    logger.info(f"Server running on http://{settings.host}:{settings.port}")
    logger.info(f"API docs: http://{settings.host}:{settings.port}/docs")
    logger.info("📝 Auto-crawling in background, data will be available soon...")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutting down...")
    
    # Stop scheduler
    try:
        stop_scheduler()
        logger.info("Scheduler stopped")
    except Exception as e:
        logger.error(f"Scheduler stop failed: {e}")
    
    logger.info("Application shutdown complete")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
