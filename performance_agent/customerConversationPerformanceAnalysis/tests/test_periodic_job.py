#!/usr/bin/env python3
"""
Test suite for Periodic Job Service
Tests the automated conversation performance analysis job functionality
"""

import unittest
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from bson import ObjectId

# Add src directory to Python path
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

from src.periodic_job_service import PeriodicJobService
from src.models import ConversationData, Tweet, Classification


class TestPeriodicJobService(unittest.TestCase):
    """Test cases for PeriodicJobService"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_mongo_uri = "mongodb://test:27017/"
        self.test_db_name = "test_csai"
        
        # Mock MongoDB client
        self.mock_client = Mock()
        self.mock_db = Mock()
        self.mock_sentiment_collection = Mock()
        self.mock_agentic_collection = Mock()
        self.mock_job_state_collection = Mock()
        
        # Setup mock return values using direct assignment
        self.mock_client.__getitem__ = Mock(return_value=self.mock_db)
        self.mock_client.admin = Mock()
        self.mock_client.admin.command = Mock(return_value={'ok': 1})
        self.mock_db.__getitem__ = Mock(side_effect=self._mock_collection_getter)
        
        # Initialize service
        with patch('src.periodic_job_service.MongoClient', return_value=self.mock_client):
            self.service = PeriodicJobService(self.mock_mongo_uri, self.test_db_name)
            self.service.client = self.mock_client
            self.service.db = self.mock_db
            self.service.sentiment_collection = self.mock_sentiment_collection
            self.service.agentic_collection = self.mock_agentic_collection
            self.service.job_state_collection = self.mock_job_state_collection
    
    def _mock_collection_getter(self, collection_name):
        """Helper to return appropriate mock collection"""
        if collection_name == 'sentiment_analysis':
            return self.mock_sentiment_collection
        elif collection_name == 'agentic_analysis':
            return self.mock_agentic_collection
        elif collection_name == 'job_state':
            return self.mock_job_state_collection
        return Mock()
    
    def test_initialization(self):
        """Test service initialization"""
        self.assertEqual(self.service.mongo_connection_string, self.mock_mongo_uri)
        self.assertEqual(self.service.db_name, self.test_db_name)
        self.assertEqual(self.service.batch_size, 50)
        self.assertEqual(self.service.job_name, "conversation_performance_analysis")
    
    def test_get_last_processed_object_id_first_run(self):
        """Test getting last processed ObjectId on first run"""
        # Mock no previous job state
        self.mock_job_state_collection.find_one.return_value = None
        
        result = self.service.get_last_processed_object_id()
        
        self.assertIsNone(result)
        self.mock_job_state_collection.find_one.assert_called_once_with(
            {"job_name": "conversation_performance_analysis"}
        )
    
    def test_get_last_processed_object_id_existing(self):
        """Test getting last processed ObjectId with existing state"""
        test_object_id = ObjectId()
        self.mock_job_state_collection.find_one.return_value = {
            "job_name": "conversation_performance_analysis",
            "last_processed_object_id": str(test_object_id)
        }
        
        result = self.service.get_last_processed_object_id()
        
        self.assertEqual(str(result), str(test_object_id))
    
    def test_update_last_processed_object_id(self):
        """Test updating last processed ObjectId"""
        test_object_id = ObjectId()
        
        self.service.update_last_processed_object_id(test_object_id)
        
        self.mock_job_state_collection.update_one.assert_called_once()
        call_args = self.mock_job_state_collection.update_one.call_args
        self.assertEqual(call_args[0][0], {"job_name": "conversation_performance_analysis"})
        self.assertEqual(call_args[1]["upsert"], True)
    
    def test_get_new_sentiment_records_first_run(self):
        """Test getting sentiment records on first run"""
        # Mock sentiment records
        test_records = [
            {"_id": ObjectId(), "conversation": {"tweets": []}},
            {"_id": ObjectId(), "conversation": {"tweets": []}}
        ]
        
        mock_cursor = Mock()
        mock_cursor.sort.return_value.limit.return_value = test_records
        self.mock_sentiment_collection.find.return_value = mock_cursor
        
        result = self.service.get_new_sentiment_records()
        
        self.assertEqual(len(result), 2)
        self.mock_sentiment_collection.find.assert_called_once_with({})
        mock_cursor.sort.assert_called_once_with("_id", 1)
        mock_cursor.sort.return_value.limit.assert_called_once_with(50)
    
    def test_get_new_sentiment_records_incremental(self):
        """Test getting sentiment records incrementally"""
        last_object_id = ObjectId()
        test_records = [{"_id": ObjectId(), "conversation": {"tweets": []}}]
        
        mock_cursor = Mock()
        mock_cursor.sort.return_value.limit.return_value = test_records
        self.mock_sentiment_collection.find.return_value = mock_cursor
        
        result = self.service.get_new_sentiment_records(last_object_id)
        
        self.assertEqual(len(result), 1)
        expected_query = {"_id": {"$gt": last_object_id}}
        self.mock_sentiment_collection.find.assert_called_once_with(expected_query)
    
    def test_convert_sentiment_to_conversation_data_success(self):
        """Test successful conversion of sentiment record to ConversationData"""
        sentiment_record = {
            "_id": ObjectId(),
            "conversation": {
                "tweets": [
                    {
                        "tweet_id": 1,
                        "author_id": "customer1",
                        "role": "Customer",
                        "inbound": True,
                        "created_at": "2023-01-01T10:00:00",
                        "text": "Hello, I need help"
                    },
                    {
                        "tweet_id": 2,
                        "author_id": "agent1",
                        "role": "Service Provider",
                        "inbound": False,
                        "created_at": "2023-01-01T10:05:00",
                        "text": "I'm here to help you"
                    }
                ],
                "classification": {
                    "categorization": "Technical Support",
                    "intent": "Technical Support",
                    "topic": "Technical",
                    "sentiment": "Neutral"
                }
            }
        }
        
        result = self.service.convert_sentiment_to_conversation_data(sentiment_record)
        
        self.assertIsInstance(result, ConversationData)
        self.assertEqual(len(result.tweets), 2)
        self.assertEqual(result.tweets[0].text, "Hello, I need help")
        self.assertEqual(result.classification.sentiment, "Neutral")
    
    def test_convert_sentiment_to_conversation_data_missing_conversation(self):
        """Test conversion with missing conversation data"""
        sentiment_record = {"_id": ObjectId()}
        
        result = self.service.convert_sentiment_to_conversation_data(sentiment_record)
        
        self.assertIsNone(result)
    
    def test_convert_sentiment_to_conversation_data_with_sentiment_analysis(self):
        """Test conversion with existing sentiment analysis results"""
        sentiment_record = {
            "_id": ObjectId(),
            "conversation": {
                "tweets": [
                    {
                        "tweet_id": 1,
                        "author_id": "customer1",
                        "role": "Customer",
                        "inbound": True,
                        "created_at": "2023-01-01T10:00:00",
                        "text": "Hello"
                    }
                ],
                "classification": {
                    "categorization": "General",
                    "intent": "Unknown",
                    "topic": "General",
                    "sentiment": "Neutral"
                }
            },
            "sentiment_analysis": {
                "overall_sentiment": "Positive",
                "intent": "Support Request",
                "topic": "Technical"
            }
        }
        
        result = self.service.convert_sentiment_to_conversation_data(sentiment_record)
        
        self.assertIsInstance(result, ConversationData)
        # Should use sentiment analysis results
        self.assertEqual(result.classification.sentiment, "Positive")
        self.assertEqual(result.classification.intent, "Support Request")
        self.assertEqual(result.classification.topic, "Technical")
    
    @patch('analyze_conversations_claude4.simulate_claude4_analysis')
    def test_simulate_performance_analysis(self, mock_simulate):
        """Test simulated performance analysis"""
        # Setup test data
        conversation_data = ConversationData(
            tweets=[
                Tweet(
                    tweet_id=1,
                    author_id="customer1",
                    role="Customer",
                    inbound=True,
                    created_at="2023-01-01T10:00:00",
                    text="Hello"
                )
            ],
            classification=Classification(
                categorization="General",
                intent="Support",
                topic="General",
                sentiment="Neutral"
            )
        )
        
        source_record = {"_id": ObjectId()}
        
        # Mock simulation result
        mock_simulate.return_value = {
            "conversation_id": "test_conv",
            "performance_metrics": {}
        }
        
        result = self.service.simulate_performance_analysis(conversation_data, source_record)
        
        self.assertIsNotNone(result)
        self.assertIn("source_object_id", result)
        self.assertIn("analysis_metadata", result)
        mock_simulate.assert_called_once()
    
    def test_persist_analysis_result(self):
        """Test persisting analysis result"""
        analysis_result = {
            "conversation_id": "test_conv",
            "performance_metrics": {},
            "analysis_metadata": {}
        }
        
        # Mock successful insertion
        mock_insert_result = Mock()
        mock_insert_result.inserted_id = ObjectId()
        self.mock_agentic_collection.insert_one.return_value = mock_insert_result
        
        result = self.service.persist_analysis_result(analysis_result)
        
        self.assertTrue(result)
        self.mock_agentic_collection.insert_one.assert_called_once()
        
        # Check that persistence metadata was added
        call_args = self.mock_agentic_collection.insert_one.call_args[0][0]
        self.assertIn("persistence_metadata", call_args)
    
    def test_run_single_batch_no_records(self):
        """Test running single batch with no new records"""
        # Mock no records to process
        mock_cursor = Mock()
        mock_cursor.sort.return_value.limit.return_value = []
        self.mock_sentiment_collection.find.return_value = mock_cursor
        
        # Mock no previous job state
        self.mock_job_state_collection.find_one.return_value = None
        
        result = self.service.run_single_batch()
        
        self.assertEqual(result["records_processed"], 0)
        self.assertEqual(result["records_analyzed"], 0)
        self.assertEqual(result["records_persisted"], 0)
        self.assertEqual(result["errors"], 0)
    
    @patch('analyze_conversations_claude4.simulate_claude4_analysis')
    def test_run_single_batch_with_records(self, mock_simulate):
        """Test running single batch with records to process"""
        # Setup test data
        test_object_id = ObjectId()
        test_records = [
            {
                "_id": test_object_id,
                "conversation": {
                    "tweets": [
                        {
                            "tweet_id": 1,
                            "author_id": "customer1",
                            "role": "Customer",
                            "inbound": True,
                            "created_at": "2023-01-01T10:00:00",
                            "text": "Hello"
                        }
                    ],
                    "classification": {
                        "categorization": "General",
                        "intent": "Support",
                        "topic": "General",
                        "sentiment": "Neutral"
                    }
                }
            }
        ]
        
        # Mock database calls
        mock_cursor = Mock()
        mock_cursor.sort.return_value.limit.return_value = test_records
        self.mock_sentiment_collection.find.return_value = mock_cursor
        self.mock_job_state_collection.find_one.return_value = None
        
        # Mock simulation result
        mock_simulate.return_value = {
            "conversation_id": "test_conv",
            "performance_metrics": {}
        }
        
        # Mock successful insertion
        mock_insert_result = Mock()
        mock_insert_result.inserted_id = ObjectId()
        self.mock_agentic_collection.insert_one.return_value = mock_insert_result
        
        result = self.service.run_single_batch()
        
        self.assertEqual(result["records_processed"], 1)
        self.assertEqual(result["records_analyzed"], 1)
        self.assertEqual(result["records_persisted"], 1)
        self.assertEqual(result["errors"], 0)
        self.assertEqual(result["last_processed_id"], str(test_object_id))
    
    def test_get_job_statistics(self):
        """Test getting job statistics"""
        # Mock job state
        test_job_state = {
            "job_name": "conversation_performance_analysis",
            "status": "completed",
            "last_updated": datetime.now()
        }
        self.mock_job_state_collection.find_one.return_value = test_job_state
        
        # Mock collection count
        self.mock_agentic_collection.count_documents.return_value = 100
        
        # Mock latest results
        test_results = [
            {
                "conversation_id": "conv_1",
                "source_object_id": str(ObjectId()),
                "analysis_metadata": {
                    "processed_timestamp": datetime.now(),
                    "model_used": "claude-4-simulated"
                }
            }
        ]
        
        mock_cursor = Mock()
        mock_cursor.sort.return_value.limit.return_value = test_results
        self.mock_agentic_collection.find.return_value = mock_cursor
        
        result = self.service.get_job_statistics()
        
        self.assertEqual(result["job_state"], test_job_state)
        self.assertEqual(result["agentic_analysis_count"], 100)
        self.assertEqual(result["latest_results_count"], 1)
    
    def test_reset_job_state(self):
        """Test resetting job state"""
        self.service.reset_job_state()
        
        self.mock_job_state_collection.delete_one.assert_called_once_with(
            {"job_name": "conversation_performance_analysis"}
        )


if __name__ == '__main__':
    unittest.main()
