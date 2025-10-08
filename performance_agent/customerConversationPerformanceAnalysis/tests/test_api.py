"""
Tests for the FastAPI endpoints
"""

import pytest
from fastapi.testclient import TestClient
from src.api import app

# Create test client
client = TestClient(app)


class TestAPIEndpoints:
    """Test cases for API endpoints"""
    
    def test_root_endpoint(self):
        """Test the root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Customer Conversation Performance Analysis API"
        assert data["version"] == "0.1.0"
        assert "docs" in data
        assert "redoc" in data
    
    def test_health_check(self):
        """Test the health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "conversation-analysis"
    
    def test_metrics_summary(self):
        """Test the metrics summary endpoint"""
        response = client.get("/metrics/summary")
        assert response.status_code == 200
        data = response.json()
        
        assert "available_metrics" in data
        assert "sentiment_mapping" in data
        assert "resolution_statuses" in data
        assert "satisfaction_levels" in data
        
        # Check specific metrics are present
        metrics = data["available_metrics"]
        expected_metrics = [
            "response_time_minutes",
            "sentiment_score", 
            "resolution_status",
            "customer_satisfaction",
            "interaction_count",
            "escalation_required"
        ]
        
        for metric in expected_metrics:
            assert metric in metrics
    
    def test_analyze_conversation_endpoint(self):
        """Test the single conversation analysis endpoint"""
        sample_conversation = {
            "tweets": [
                {
                    "tweet_id": 1081018,
                    "author_id": "129629",
                    "role": "Customer",
                    "inbound": True,
                    "created_at": "Mon Oct 23 19:44:24 +0000 2017",
                    "text": "I'm tired of the spam calls. Y'all are trash @sprintcare"
                },
                {
                    "tweet_id": 1081017,
                    "author_id": "sprintcare",
                    "role": "Service Provider",
                    "inbound": False,
                    "created_at": "Mon Oct 23 19:57:11 +0000 2017",
                    "text": "@129629 This is not the kind of feed back we like to receive. Please send us a Direct Message, so that we can further assist you. -TR"
                }
            ],
            "classification": {
                "categorization": "Complaint about unwanted calls",
                "intent": "Complaint",
                "topic": "General",
                "sentiment": "Negative"
            }
        }
        
        response = client.post("/analyze", json=sample_conversation)
        assert response.status_code == 200
        
        data = response.json()
        assert "tweets" in data
        assert "classification" in data
        assert "performance_metrics" in data
        
        # Verify original data is preserved
        assert len(data["tweets"]) == 2
        assert data["classification"]["sentiment"] == "Negative"
        
        # Verify performance metrics are added
        metrics = data["performance_metrics"]
        assert "response_time_minutes" in metrics
        assert "sentiment_score" in metrics
        assert "resolution_status" in metrics
        assert "customer_satisfaction" in metrics
        assert "interaction_count" in metrics
        assert "escalation_required" in metrics
        
        # Verify specific metric values
        assert metrics["interaction_count"] == 2
        assert metrics["sentiment_score"] == -1.0  # Negative sentiment
        assert isinstance(metrics["escalation_required"], bool)
    
    def test_analyze_conversation_with_positive_sentiment(self):
        """Test analysis with positive sentiment conversation"""
        sample_conversation = {
            "tweets": [
                {
                    "tweet_id": 1081020,
                    "author_id": "customer123",
                    "role": "Customer",
                    "inbound": True,
                    "created_at": "Mon Oct 23 20:00:00 +0000 2017",
                    "text": "Thank you for the quick help with my account issue!"
                },
                {
                    "tweet_id": 1081021,
                    "author_id": "support",
                    "role": "Service Provider",
                    "inbound": False,
                    "created_at": "Mon Oct 23 20:05:00 +0000 2017",
                    "text": "@customer123 You're welcome! We're glad we could resolve this quickly for you."
                }
            ],
            "classification": {
                "categorization": "Account assistance",
                "intent": "Support Request",
                "topic": "Account",
                "sentiment": "Positive"
            }
        }
        
        response = client.post("/analyze", json=sample_conversation)
        assert response.status_code == 200
        
        data = response.json()
        metrics = data["performance_metrics"]
        
        assert metrics["sentiment_score"] == 1.0  # Positive sentiment
        assert metrics["customer_satisfaction"] == "High"
        assert metrics["escalation_required"] == False
    
    def test_batch_analysis_endpoint(self):
        """Test the batch conversation analysis endpoint"""
        sample_conversations = [
            {
                "tweets": [
                    {
                        "tweet_id": 1,
                        "author_id": "customer1",
                        "role": "Customer",
                        "inbound": True,
                        "created_at": "Mon Oct 23 19:00:00 +0000 2017",
                        "text": "Need help with my order"
                    }
                ],
                "classification": {
                    "categorization": "Order inquiry",
                    "intent": "Support Request",
                    "topic": "Orders",
                    "sentiment": "Neutral"
                }
            },
            {
                "tweets": [
                    {
                        "tweet_id": 2,
                        "author_id": "customer2",
                        "role": "Customer",
                        "inbound": True,
                        "created_at": "Mon Oct 23 19:30:00 +0000 2017",
                        "text": "Great service, thanks!"
                    }
                ],
                "classification": {
                    "categorization": "Positive feedback",
                    "intent": "Compliment",
                    "topic": "Service",
                    "sentiment": "Positive"
                }
            }
        ]
        
        response = client.post("/analyze/batch", json=sample_conversations)
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 2
        
        # Verify each conversation has performance metrics
        for conversation_result in data:
            assert "tweets" in conversation_result
            assert "classification" in conversation_result
            assert "performance_metrics" in conversation_result
    
    def test_analyze_conversation_invalid_data(self):
        """Test conversation analysis with invalid data"""
        invalid_conversation = {
            "tweets": [],  # Empty tweets array
            "classification": {
                "categorization": "Test",
                "intent": "Test",
                "topic": "Test",
                "sentiment": "Invalid"  # Invalid sentiment
            }
        }
        
        response = client.post("/analyze", json=invalid_conversation)
        # Should still process but handle gracefully
        assert response.status_code in [200, 422]  # Either processes or validation error
    
    def test_analyze_conversation_missing_fields(self):
        """Test conversation analysis with missing required fields"""
        invalid_conversation = {
            "tweets": [
                {
                    "tweet_id": 1,
                    "author_id": "test",
                    "role": "Customer",
                    # Missing required fields
                }
            ]
        }
        
        response = client.post("/analyze", json=invalid_conversation)
        assert response.status_code == 422  # Validation error
    
    def test_batch_analysis_with_mixed_valid_invalid(self):
        """Test batch analysis with mix of valid and invalid conversations"""
        mixed_conversations = [
            {
                "tweets": [
                    {
                        "tweet_id": 1,
                        "author_id": "customer1",
                        "role": "Customer",
                        "inbound": True,
                        "created_at": "Mon Oct 23 19:00:00 +0000 2017",
                        "text": "Valid conversation"
                    }
                ],
                "classification": {
                    "categorization": "Valid",
                    "intent": "Support Request",
                    "topic": "Test",
                    "sentiment": "Neutral"
                }
            },
            {
                "tweets": [],  # Invalid - empty tweets
                "classification": {
                    "categorization": "Invalid",
                    "intent": "Test",
                    "topic": "Test",
                    "sentiment": "Negative"
                }
            }
        ]
        
        response = client.post("/analyze/batch", json=mixed_conversations)
        # Should handle mixed scenarios appropriately
        assert response.status_code in [200, 400]


if __name__ == "__main__":
    pytest.main([__file__])
