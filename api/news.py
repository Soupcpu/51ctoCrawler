"""News API endpoints"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional
import logging
from datetime import datetime

from models.news import NewsResponse, NewsArticle
from core.cache import get_news_cache
from core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/news", tags=["news"])


@router.get("/", response_model=NewsResponse)
async def get_news(
    page: int = 1,
    page_size: int = 20,
    category: Optional[str] = None,
    search: Optional[str] = None,
    all: bool = False
):
    """Get news list with pagination and filtering"""
    try:
        cache = get_news_cache()
        
        if all:
            page_size = 10000
        
        result = cache.get_news(
            page=page,
            page_size=page_size,
            category=category,
            search=search
        )
        
        if all:
            result.page_size = result.total
        
        return result
    except Exception as e:
        logger.error(f"Get news failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{article_id}")
async def get_article(article_id: str):
    """Get single article by ID"""
    try:
        cache = get_news_cache()
        result = cache.get_news(page=1, page_size=10000)
        
        for article in result.articles:
            if article.id == article_id:
                return article
        
        raise HTTPException(status_code=404, detail="Article not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get article failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/crawl")
async def crawl_news(background_tasks: BackgroundTasks, max_pages: Optional[int] = None):
    """Manually trigger news crawling"""
    try:
        from services.cto51_crawler import CTO51Crawler
        from models.news import NewsArticle
        
        def crawl_task():
            logger.info("Starting crawl task...")
            crawler = CTO51Crawler(min_article_id=settings.min_article_id)
            cache = get_news_cache()
            
            def batch_callback(articles):
                try:
                    news_articles = [NewsArticle(**article) for article in articles]
                    cache.append_to_cache(news_articles)
                    logger.info(f"Batch saved: {len(news_articles)} articles")
                except Exception as e:
                    logger.error(f"Batch save failed: {e}")
            
            articles = crawler.crawl_all_pages(
                max_pages=max_pages or settings.max_pages,
                batch_callback=batch_callback,
                batch_size=5
            )
            
            logger.info(f"Crawl task completed: {len(articles)} articles")
        
        background_tasks.add_task(crawl_task)
        
        return {
            "message": "Crawl task started",
            "max_pages": max_pages or settings.max_pages,
            "timestamp": datetime.now().isoformat(),
            "note": "Crawling in background, check cache status later"
        }
    except Exception as e:
        logger.error(f"Start crawl task failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/info")
async def get_status():
    """Get service status"""
    try:
        cache = get_news_cache()
        cache_status = cache.get_status()
        
        return {
            "service_status": cache_status,
            "source": {
                "name": "51CTO",
                "identifier": "51CTO",
                "category": "技术文章"
            },
            "timestamp": datetime.now().isoformat(),
            "endpoints": {
                "all_news": "/api/news/",
                "news_detail": "/api/news/{article_id}",
                "manual_crawl": "/api/news/crawl",
                "service_status": "/api/news/status/info",
                "cache_refresh": "/api/news/cache/refresh"
            }
        }
    except Exception as e:
        logger.error(f"Get status failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cache/refresh")
async def refresh_cache(background_tasks: BackgroundTasks):
    """Manually refresh cache"""
    try:
        from services.cto51_crawler import CTO51Crawler
        from models.news import NewsArticle
        
        def refresh_task():
            logger.info("Starting cache refresh...")
            crawler = CTO51Crawler(min_article_id=settings.min_article_id)
            cache = get_news_cache()
            
            articles = crawler.crawl_all_pages(
                max_pages=settings.max_pages,
                batch_size=5
            )
            
            news_articles = [NewsArticle(**article) for article in articles]
            cache.update_cache(news_articles)
            logger.info(f"Cache refreshed: {len(news_articles)} articles")
        
        background_tasks.add_task(refresh_task)
        
        return {
            "message": "Cache refresh started",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Refresh cache failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
