"""
Data models for the Customer Conversation Performance Analysis API
"""

from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime


class Tweet(BaseModel):
    """Model for individual tweet data"""
    tweet_id: int
    author_id: str
    role: str  # "Customer" or "Service Provider"
    inbound: bool
    created_at: str  # ISO format datetime string
    text: str


class Classification(BaseModel):
    """Model for conversation classification data"""
    categorization: str
    intent: str
    topic: str
    sentiment: str


class ConversationData(BaseModel):
    """Model for complete conversation data with tweets and classification"""
    tweets: List[Tweet]
    classification: Classification


class ConversationResponse(BaseModel):
    """Model for API response containing processed conversation data"""
    tweets: List[Tweet]
    classification: Classification
    performance_metrics: Optional[dict] = None


class PerformanceMetrics(BaseModel):
    """Model for performance analysis metrics"""
    response_time_minutes: Optional[float] = None
    sentiment_score: Optional[float] = None
    resolution_status: Optional[str] = None
    customer_satisfaction: Optional[str] = None
    interaction_count: int = 0
    escalation_required: bool = False
