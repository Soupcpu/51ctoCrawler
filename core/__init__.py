"""Core modules"""
from .config import settings
from .cache import get_news_cache, init_cache
from .logging_config import setup_logging
from .scheduler import get_scheduler, start_scheduler, stop_scheduler

__all__ = ['settings', 'get_news_cache', 'init_cache', 'setup_logging', 
           'get_scheduler', 'start_scheduler', 'stop_scheduler']
