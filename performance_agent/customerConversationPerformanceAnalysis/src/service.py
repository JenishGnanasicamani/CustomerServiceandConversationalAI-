"""
Service layer for conversation performance analysis
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta
import re
from .models import ConversationData, ConversationResponse, PerformanceMetrics, Tweet, Classification


class ConversationAnalysisService:
    """Service for analyzing conversation performance metrics"""
    
    def __init__(self):
        self.sentiment_scores = {
            "Positive": 1.0,
            "Neutral": 0.0,
            "Negative": -1.0
        }
    
    def analyze_conversation(self, conversation_data: ConversationData) -> ConversationResponse:
        """
        Analyze conversation data and return enhanced response with performance metrics
        
        Args:
            conversation_data: Input conversation data with tweets and classification
            
        Returns:
            ConversationResponse with original data plus performance metrics
        """
        performance_metrics = self._calculate_performance_metrics(conversation_data)
        
        return ConversationResponse(
            tweets=conversation_data.tweets,
            classification=conversation_data.classification,
            performance_metrics=performance_metrics.model_dump()
        )
    
    def _calculate_performance_metrics(self, conversation_data: ConversationData) -> PerformanceMetrics:
        """Calculate performance metrics for the conversation"""
        
        tweets = conversation_data.tweets
        classification = conversation_data.classification
        
        # Sort tweets by creation time
        sorted_tweets = sorted(tweets, key=lambda x: self._parse_datetime(x.created_at))
        
        # Calculate response time
        response_time = self._calculate_response_time(sorted_tweets)
        
        # Get sentiment score
        sentiment_score = self.sentiment_scores.get(classification.sentiment, 0.0)
        
        # Determine resolution status
        resolution_status = self._determine_resolution_status(sorted_tweets, classification)
        
        # Calculate customer satisfaction
        customer_satisfaction = self._calculate_customer_satisfaction(classification, response_time)
        
        # Check if escalation is required
        escalation_required = self._check_escalation_required(classification, sorted_tweets)
        
        return PerformanceMetrics(
            response_time_minutes=response_time,
            sentiment_score=sentiment_score,
            resolution_status=resolution_status,
            customer_satisfaction=customer_satisfaction,
            interaction_count=len(tweets),
            escalation_required=escalation_required
        )
    
    def _parse_datetime(self, date_string: str) -> datetime:
        """Parse datetime string from tweet created_at field"""
        try:
            # Handle format: "Mon Oct 23 19:44:24 +0000 2017"
            return datetime.strptime(date_string, "%a %b %d %H:%M:%S %z %Y")
        except ValueError:
            # Fallback for other formats
            try:
                return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            except ValueError:
                return datetime.now()
    
    def _calculate_response_time(self, sorted_tweets: List[Tweet]) -> float:
        """Calculate average response time between customer and service provider"""
        if len(sorted_tweets) < 2:
            return 0.0
        
        response_times = []
        
        for i in range(len(sorted_tweets) - 1):
            current_tweet = sorted_tweets[i]
            next_tweet = sorted_tweets[i + 1]
            
            # Check if this is a customer -> service provider interaction
            if (current_tweet.role == "Customer" and 
                next_tweet.role == "Service Provider"):
                
                current_time = self._parse_datetime(current_tweet.created_at)
                next_time = self._parse_datetime(next_tweet.created_at)
                
                response_time = (next_time - current_time).total_seconds() / 60.0
                response_times.append(response_time)
        
        return sum(response_times) / len(response_times) if response_times else 0.0
    
    def _determine_resolution_status(self, tweets: List[Tweet], classification: Classification) -> str:
        """Determine if the conversation appears to be resolved"""
        
        service_provider_tweets = [t for t in tweets if t.role == "Service Provider"]
        
        if not service_provider_tweets:
            return "Unresolved"
        
        last_service_tweet = service_provider_tweets[-1].text.lower()
        
        # Check for resolution indicators
        resolution_keywords = [
            "resolved", "fixed", "solved", "completed", "closed",
            "thank you", "glad to help", "issue has been"
        ]
        
        if any(keyword in last_service_tweet for keyword in resolution_keywords):
            return "Resolved"
        
        # Check for pending actions
        pending_keywords = [
            "please", "could you", "can you", "we need", "follow up",
            "direct message", "dm us", "contact us"
        ]
        
        if any(keyword in last_service_tweet for keyword in pending_keywords):
            return "Pending"
        
        return "In Progress"
    
    def _calculate_customer_satisfaction(self, classification: Classification, response_time: float) -> str:
        """Estimate customer satisfaction based on sentiment and response time"""
        
        sentiment = classification.sentiment
        
        if sentiment == "Positive":
            return "High"
        elif sentiment == "Neutral":
            # Consider response time for neutral sentiment
            if response_time <= 30:  # 30 minutes or less
                return "Medium"
            else:
                return "Low"
        else:  # Negative
            # Even negative sentiment can have medium satisfaction with quick response
            if response_time <= 15:  # Very quick response
                return "Medium"
            else:
                return "Low"
    
    def _check_escalation_required(self, classification: Classification, tweets: List[Tweet]) -> bool:
        """Check if escalation is required based on various factors"""
        
        # Check for escalation keywords
        escalation_keywords = [
            "manager", "supervisor", "escalate", "complaint", "unacceptable",
            "terrible", "awful", "worst", "cancel", "legal", "lawsuit"
        ]
        
        all_text = " ".join([tweet.text.lower() for tweet in tweets])
        
        if any(keyword in all_text for keyword in escalation_keywords):
            return True
        
        # Check if multiple complaints with negative sentiment
        if (classification.intent == "Complaint" and 
            classification.sentiment == "Negative" and 
            len(tweets) > 3):
            return True
        
        return False


# Global service instance
conversation_service = ConversationAnalysisService()
