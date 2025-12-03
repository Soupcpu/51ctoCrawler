"""Configuration settings"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""
    # App
    app_name: str = "51CTO Backend API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8002
    
    # CORS
    cors_origins: List[str] = ["*"]
    
    # Crawler
    min_article_id: int = 33500  # 主要控制：爬取到此 ID 为止
    crawler_delay: float = 2.0
    max_pages: int = 999  # 备用限制：最大页数（通常不会达到）
    
    # Cache
    enable_cache: bool = True
    cache_update_interval: int = 3600  # 1 hour
    cache_initial_load: bool = True  # Auto crawl on startup
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/app.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
