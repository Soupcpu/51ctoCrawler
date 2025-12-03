"""Run script"""
import uvicorn
from core.config import settings

if __name__ == "__main__":
    print("="*60)
    print("51CTO Backend API - Starting...")
    print("="*60)
    print(f"Server: http://{settings.host}:{settings.port}")
    print(f"API Docs: http://{settings.host}:{settings.port}/docs")
    print(f"ReDoc: http://{settings.host}:{settings.port}/redoc")
    print("="*60)
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
