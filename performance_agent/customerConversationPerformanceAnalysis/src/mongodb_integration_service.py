"""
MongoDB Integration Service for Performance Analysis

This service handles reading conversation data from MongoDB, processing it through
the performance analysis system, and storing results back to MongoDB.
"""

import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from .models import ConversationData, Tweet, Classification
from .llm_agent_service import get_llm_agent_service


class MongoDBIntegrationService:
    """Service for integrating performance analysis with MongoDB"""
    
    def __init__(self):
        """Initialize the MongoDB integration service"""
        self.logger = logging.getLogger(__name__)
        self.performance_service = None
        
    def _get_performance_service(self):
        """Lazy initialization of performance analysis service"""
        if self.performance_service is None:
            try:
                self.performance_service = get_llm_agent_service()
                self.logger.info("Performance analysis service initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize performance service: {e}")
                raise
        return self.performance_service
    
    def convert_mongo_document_to_conversation_data(self, mongo_doc: Dict[str, Any]) -> ConversationData:
        """
        Convert MongoDB document to ConversationData model
        
        Args:
            mongo_doc: Document from MongoDB sentimental_analysis collection
            
        Returns:
            ConversationData object
        """
        try:
            # Convert tweets
            tweets = []
            for tweet_data in mongo_doc.get('tweets', []):
                tweet = Tweet(
                    tweet_id=tweet_data.get('tweet_id'),
                    author_id=tweet_data.get('author_id'),
                    role=tweet_data.get('role', 'Unknown'),
                    inbound=tweet_data.get('inbound', True),
                    created_at=tweet_data.get('created_at', ''),
                    text=tweet_data.get('text', '')
                )
                tweets.append(tweet)
            
            # Convert classification
            classification_data = mongo_doc.get('classification', {})
            classification = Classification(
                categorization=classification_data.get('categorization', 'Unknown'),
                intent=classification_data.get('intent', 'Unknown'),
                topic=classification_data.get('topic', 'Unknown'),
                sentiment=classification_data.get('sentiment', 'Neutral')
            )
            
            # Create ConversationData with proper conversation_id extraction
            conversation_data = ConversationData(tweets=tweets, classification=classification)
            
            # Add conversation_number/conversation_id to the ConversationData object for proper tracking
            # This ensures the ID is properly passed through the analysis pipeline
            if hasattr(conversation_data, '__dict__'):
                conversation_data.conversation_number = mongo_doc.get('conversation_number')
                conversation_data.conversation_id = (
                    mongo_doc.get('conversation_number') or 
                    mongo_doc.get('conversation_id') or
                    f"conv_{mongo_doc.get('_id')}"
                )
            
            return conversation_data
            
        except Exception as e:
            self.logger.error(f"Error converting MongoDB document to ConversationData: {e}")
            self.logger.error(f"Document: {mongo_doc}")
            raise
    
    def create_analysis_result_document(
        self, 
        original_doc: Dict[str, Any], 
        analysis_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create the document to be stored in agentic_analysis collection
        
        Args:
            original_doc: Original document from sentimental_analysis
            analysis_results: Results from performance analysis
            
        Returns:
            Document ready for insertion into agentic_analysis collection
        """
        try:
            # Create the result document
            result_doc = {
                # Original conversation data
                "conversation_number": original_doc.get("conversation_number"),
                "original_id": str(original_doc.get("_id")),
                "tweets": original_doc.get("tweets", []),
                "classification": original_doc.get("classification", {}),
                
                # Performance analysis results
                "performance_analysis": analysis_results,
                
                # Metadata
                "analysis_metadata": {
                    "analyzed_at": datetime.utcnow().isoformat(),
                    "analysis_version": "2.0.0",
                    "analysis_method": analysis_results.get("analysis_method", "LLM-based Agent Analysis"),
                    "model_used": analysis_results.get("model_used", "gpt-4"),
                    "conversation_id": analysis_results.get("conversation_id")
                }
            }
            
            return result_doc
            
        except Exception as e:
            self.logger.error(f"Error creating analysis result document: {e}")
            raise
    
    def process_conversations_batch(
        self, 
        conversations: List[Dict[str, Any]], 
        batch_number: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Process a batch of conversations through performance analysis
        
        Args:
            conversations: List of conversation documents from MongoDB
            batch_number: Batch number for logging
            
        Returns:
            List of processed documents ready for insertion
        """
        performance_service = self._get_performance_service()
        processed_documents = []
        
        self.logger.info(f"Processing batch {batch_number} with {len(conversations)} conversations")
        
        for i, conversation_doc in enumerate(conversations, 1):
            try:
                # Convert to ConversationData model
                conversation_data = self.convert_mongo_document_to_conversation_data(conversation_doc)
                
                # Perform comprehensive performance analysis
                self.logger.info(f"Analyzing conversation {i}/{len(conversations)} (ID: {conversation_doc.get('_id')})")
                analysis_results = performance_service.analyze_conversation_performance(conversation_data)
                
                # Create the result document
                result_doc = self.create_analysis_result_document(conversation_doc, analysis_results)
                processed_documents.append(result_doc)
                
                self.logger.info(f"Successfully analyzed conversation {i}/{len(conversations)}")
                
            except Exception as e:
                self.logger.error(f"Error processing conversation {i}/{len(conversations)}: {e}")
                self.logger.error(f"Conversation ID: {conversation_doc.get('_id')}")
                
                # Create error document
                error_doc = {
                    "conversation_number": conversation_doc.get("conversation_number"),
                    "original_id": str(conversation_doc.get("_id")),
                    "tweets": conversation_doc.get("tweets", []),
                    "classification": conversation_doc.get("classification", {}),
                    "performance_analysis": {
                        "error": f"Analysis failed: {str(e)}",
                        "analysis_timestamp": datetime.utcnow().isoformat(),
                        "analysis_method": "Failed",
                        "conversation_id": f"error_{conversation_doc.get('_id')}"
                    },
                    "analysis_metadata": {
                        "analyzed_at": datetime.utcnow().isoformat(),
                        "analysis_version": "2.0.0",
                        "analysis_method": "Failed",
                        "error": str(e)
                    }
                }
                processed_documents.append(error_doc)
        
        return processed_documents
    
    def extract_summary_statistics(self, analysis_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract summary statistics from processed conversations
        
        Args:
            analysis_results: List of processed conversation documents
            
        Returns:
            Summary statistics
        """
        try:
            total_conversations = len(analysis_results)
            successful_analyses = sum(1 for doc in analysis_results 
                                    if "error" not in doc.get("performance_analysis", {}))
            failed_analyses = total_conversations - successful_analyses
            
            # Extract sentiment distribution
            sentiment_counts = {}
            for doc in analysis_results:
                sentiment = doc.get("classification", {}).get("sentiment", "Unknown")
                sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
            
            # Extract topic distribution
            topic_counts = {}
            for doc in analysis_results:
                topic = doc.get("classification", {}).get("topic", "Unknown")
                topic_counts[topic] = topic_counts.get(topic, 0) + 1
            
            summary = {
                "processing_summary": {
                    "total_conversations": total_conversations,
                    "successful_analyses": successful_analyses,
                    "failed_analyses": failed_analyses,
                    "success_rate": (successful_analyses / total_conversations) * 100 if total_conversations > 0 else 0
                },
                "conversation_distribution": {
                    "by_sentiment": sentiment_counts,
                    "by_topic": topic_counts
                },
                "processing_metadata": {
                    "processed_at": datetime.utcnow().isoformat(),
                    "batch_size": total_conversations
                }
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error extracting summary statistics: {e}")
            return {
                "error": f"Failed to extract summary: {str(e)}",
                "processed_at": datetime.utcnow().isoformat()
            }


def create_mongodb_integration_service() -> MongoDBIntegrationService:
    """Factory function to create MongoDB integration service"""
    return MongoDBIntegrationService()


# MongoDB integration functions for external use
def process_all_conversations_from_mongo(
    fetch_function,
    store_function,
    batch_size: int = 50
) -> Dict[str, Any]:
    """
    Process all conversations from MongoDB sentimental_analysis collection
    
    Args:
        fetch_function: Function to fetch conversations from MongoDB
        store_function: Function to store results to MongoDB
        batch_size: Number of conversations to process in each batch
        
    Returns:
        Processing summary and statistics
    """
    service = create_mongodb_integration_service()
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Starting MongoDB conversation processing")
        
        # Fetch all conversations
        logger.info("Fetching conversations from sentimental_analysis collection")
        conversations = fetch_function()
        
        if not conversations:
            logger.warning("No conversations found in sentimental_analysis collection")
            return {
                "status": "completed",
                "message": "No conversations to process",
                "processing_summary": {
                    "total_conversations": 0,
                    "successful_analyses": 0,
                    "failed_analyses": 0,
                    "success_rate": 0
                }
            }
        
        logger.info(f"Found {len(conversations)} conversations to process")
        
        # Process in batches
        all_processed_documents = []
        total_batches = (len(conversations) + batch_size - 1) // batch_size
        
        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min((batch_num + 1) * batch_size, len(conversations))
            batch_conversations = conversations[start_idx:end_idx]
            
            logger.info(f"Processing batch {batch_num + 1}/{total_batches}")
            processed_batch = service.process_conversations_batch(
                batch_conversations, 
                batch_num + 1
            )
            
            # Store batch results
            if processed_batch:
                logger.info(f"Storing {len(processed_batch)} processed conversations to agentic_analysis")
                store_function(processed_batch)
            
            all_processed_documents.extend(processed_batch)
        
        # Generate summary statistics
        summary = service.extract_summary_statistics(all_processed_documents)
        
        logger.info("MongoDB conversation processing completed successfully")
        logger.info(f"Processed {summary['processing_summary']['total_conversations']} conversations")
        logger.info(f"Success rate: {summary['processing_summary']['success_rate']:.2f}%")
        
        return {
            "status": "completed",
            "message": "All conversations processed successfully",
            **summary
        }
    
    except Exception as e:
        logger.error(f"Error in MongoDB conversation processing: {e}")
        return {
            "status": "failed",
            "error": str(e),
            "message": "Processing failed with errors"
        }
