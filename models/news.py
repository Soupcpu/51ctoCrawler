"""News data models"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class ContentType(str, Enum):
    """Content block types"""
    TEXT = "text"
    IMAGE = "image"
    CODE = "code"
    VIDEO = "video"


class NewsContentBlock(BaseModel):
    """News content block"""
    type: ContentType
    value: str
    language: Optional[str] = None  # For code blocks: python, javascript, etc.


class NewsArticle(BaseModel):
    """News article model"""
    id: Optional[str] = None
    title: str
    date: str
    url: str
    content: List[NewsContentBlock]
    category: Optional[str] = None
    summary: Optional[str] = None
    source: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class NewsResponse(BaseModel):
    """News list response"""
    articles: List[NewsArticle]
    total: int
    page: int
    page_size: int
    has_next: bool = Field(False, description="Has next page")
    has_prev: bool = Field(False, description="Has previous page")
