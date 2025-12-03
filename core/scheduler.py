"""Task scheduler - Auto crawl on startup"""
import logging
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from .cache import get_news_cache, ServiceStatus
from .config import settings

logger = logging.getLogger(__name__)


class TaskScheduler:
    """Task scheduler for auto crawling"""
    
    def __init__(self):
        self.thread_pool = ThreadPoolExecutor(max_workers=2, thread_name_prefix="CrawlerWorker")
        self._initial_crawl_done = False
    
    def _run_crawler_in_thread(self, task_name: str):
        """Run crawler in background thread"""
        try:
            logger.info(f"🚀 Starting {task_name}...")
            
            from services.cto51_crawler import CTO51Crawler
            from models.news import NewsArticle
            
            cache = get_news_cache()
            crawler = CTO51Crawler(min_article_id=settings.min_article_id)
            
            # Batch callback to save data incrementally
            def batch_callback(articles):
                try:
                    news_articles = [NewsArticle(**article) for article in articles]
                    cache.append_to_cache(news_articles)
                    logger.info(f"📝 [{task_name}] Saved {len(news_articles)} articles to cache and file")
                except Exception as e:
                    logger.error(f"❌ [{task_name}] Batch save failed: {e}")
            
            # Start crawling
            articles = crawler.crawl_all_pages(
                max_pages=settings.max_pages,
                batch_callback=batch_callback,
                batch_size=5
            )
            
            logger.info(f"✅ {task_name} completed: {len(articles)} articles")
            logger.info(f"💾 All data saved to: {crawler.data_file}")
            
            # Mark as done
            self._initial_crawl_done = True
            
        except KeyboardInterrupt:
            logger.warning(f"⚠️ {task_name} interrupted by user")
            logger.info(f"💾 Data has been saved incrementally during crawling")
            
        except Exception as e:
            logger.error(f"❌ {task_name} failed: {e}")
            logger.info(f"💾 Data saved incrementally before error")
            import traceback
            traceback.print_exc()
    
    async def initial_cache_load(self):
        """Initial cache load on startup"""
        try:
            logger.info("="*60)
            logger.info("🔄 Starting initial cache load...")
            logger.info("="*60)
            
            # First, try to load existing data from file
            cache = get_news_cache()
            data_file = "data/51cto_articles.json"
            
            try:
                import os
                import json
                if os.path.exists(data_file):
                    logger.info(f"📂 Loading existing data from {data_file}...")
                    with open(data_file, 'r', encoding='utf-8') as f:
                        existing_articles = json.load(f)
                    
                    if existing_articles:
                        from models.news import NewsArticle
                        news_articles = [NewsArticle(**article) for article in existing_articles]
                        cache.update_cache(news_articles)
                        logger.info(f"✅ Loaded {len(news_articles)} articles from file")
                        logger.info(f"📊 Cache is ready with existing data")
                    else:
                        logger.info(f"📝 Data file is empty")
                else:
                    logger.info(f"📝 No existing data file found")
            except Exception as e:
                logger.warning(f"⚠️ Failed to load existing data: {e}")
            
            # Then submit crawler task to background thread
            future = self.thread_pool.submit(
                self._run_crawler_in_thread,
                "Initial Crawl"
            )
            
            logger.info("✅ Initial crawl task submitted to background thread")
            logger.info("📊 Server is ready to accept requests")
            logger.info("📝 Crawling in background, will update with new articles")
            logger.info("="*60)
            
        except Exception as e:
            logger.error(f"❌ Initial cache load failed: {e}")
            cache = get_news_cache()
            cache.set_status(ServiceStatus.ERROR, str(e))
    
    def shutdown(self):
        """Shutdown scheduler"""
        try:
            logger.info("Shutting down scheduler...")
            self.thread_pool.shutdown(wait=False)
            logger.info("Scheduler shutdown complete")
        except Exception as e:
            logger.error(f"Scheduler shutdown error: {e}")


# Global scheduler instance
_scheduler: TaskScheduler = None


def get_scheduler() -> TaskScheduler:
    """Get scheduler instance"""
    global _scheduler
    if _scheduler is None:
        _scheduler = TaskScheduler()
    return _scheduler


def start_scheduler():
    """Start scheduler"""
    global _scheduler
    _scheduler = TaskScheduler()
    logger.info("Scheduler started")


def stop_scheduler():
    """Stop scheduler"""
    global _scheduler
    if _scheduler:
        _scheduler.shutdown()
        _scheduler = None
