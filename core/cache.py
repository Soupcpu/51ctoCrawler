"""Cache management"""
import logging
import threading
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from models.news import NewsArticle, NewsResponse

logger = logging.getLogger(__name__)


class ServiceStatus(str, Enum):
    """Service status"""
    READY = "ready"
    PREPARING = "preparing"
    ERROR = "error"


class NewsCache:
    """News cache manager"""
    
    def __init__(self):
        self._cache: List[NewsArticle] = []
        self._cache_lock = threading.RLock()
        self._status = ServiceStatus.PREPARING
        self._last_update = None
        self._error_message = None
        
    def get_status(self) -> Dict[str, Any]:
        """Get cache status"""
        with self._cache_lock:
            return {
                "status": self._status.value,
                "last_update": self._last_update,
                "cache_count": len(self._cache),
                "error_message": self._error_message
            }
    
    def set_status(self, status: ServiceStatus, error_message: Optional[str] = None):
        """Set cache status"""
        with self._cache_lock:
            self._status = status
            self._error_message = error_message
            logger.info(f"Cache status updated: {status.value}")
    
    def get_news(self, page: int = 1, page_size: int = 20,
                 category: Optional[str] = None,
                 search: Optional[str] = None) -> NewsResponse:
        """Get news with pagination and filtering"""
        with self._cache_lock:
            if self._status == ServiceStatus.ERROR:
                raise Exception(f"Service error: {self._error_message}")
            
            # Filter data
            filtered_news = self._cache.copy()
            
            # Category filter
            if category:
                filtered_news = [news for news in filtered_news if news.category == category]
            
            # Search filter
            if search:
                search_lower = search.lower()
                filtered_news = [
                    news for news in filtered_news
                    if search_lower in news.title.lower() or
                       (news.summary and search_lower in news.summary.lower())
                ]
            
            # Sort by date (newest first)
            try:
                filtered_news.sort(key=lambda x: x.date, reverse=True)
            except:
                pass
            
            # Pagination
            total = len(filtered_news)
            start = (page - 1) * page_size
            end = start + page_size
            paginated_news = filtered_news[start:end]
            
            return NewsResponse(
                articles=paginated_news,
                total=total,
                page=page,
                page_size=page_size,
                has_next=end < total,
                has_prev=page > 1
            )
    
    def update_cache(self, news_data: List[NewsArticle]):
        """Update cache data"""
        with self._cache_lock:
            try:
                self.set_status(ServiceStatus.PREPARING)
                self._cache = news_data
                self._last_update = datetime.now().isoformat()
                self.set_status(ServiceStatus.READY)
                logger.info(f"Cache updated successfully, {len(news_data)} articles")
            except Exception as e:
                error_msg = f"Cache update failed: {str(e)}"
                self.set_status(ServiceStatus.ERROR, error_msg)
                logger.error(error_msg)
                raise
    
    def append_to_cache(self, new_articles: List[NewsArticle]):
        """Append new articles to cache"""
        with self._cache_lock:
            try:
                existing_urls = {article.url for article in self._cache}
                unique_articles = [
                    article for article in new_articles
                    if article.url not in existing_urls
                ]
                
                if unique_articles:
                    self._cache.extend(unique_articles)
                    self._last_update = datetime.now().isoformat()
                    
                    if len(self._cache) > 0 and self._status == ServiceStatus.PREPARING:
                        self.set_status(ServiceStatus.READY)
                    
                    logger.info(f"Appended {len(unique_articles)} new articles to cache")
            except Exception as e:
                logger.error(f"Failed to append to cache: {e}")
                raise
    
    def clear_cache(self):
        """Clear cache"""
        with self._cache_lock:
            self._cache.clear()
            self._last_update = None
            self.set_status(ServiceStatus.PREPARING)
            logger.info("Cache cleared")


# Global cache instance
_news_cache: Optional[NewsCache] = None


def get_news_cache() -> NewsCache:
    """Get news cache instance"""
    global _news_cache
    if _news_cache is None:
        _news_cache = NewsCache()
    return _news_cache


def init_cache():
    """Initialize cache"""
    global _news_cache
    _news_cache = NewsCache()
    logger.info("Cache initialized")
