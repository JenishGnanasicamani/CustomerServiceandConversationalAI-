"""
FastAPI application for Customer Conversation Performance Analysis
"""

from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from .models import ConversationData, ConversationResponse
from .service import conversation_service

# Create FastAPI application
app = FastAPI(
    title="Customer Conversation Performance Analysis API",
    description="API for analyzing customer service conversation performance metrics",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint providing API information"""
    return {
        "message": "Customer Conversation Performance Analysis API",
        "version": "0.1.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "conversation-analysis"}


@app.post("/analyze", response_model=ConversationResponse)
async def analyze_conversation(conversation_data: ConversationData):
    """
    Analyze a single conversation and return performance metrics
    
    Args:
        conversation_data: Conversation data containing tweets and classification
        
    Returns:
        ConversationResponse with original data plus performance metrics
        
    Raises:
        HTTPException: If there's an error processing the conversation data
    """
    try:
        result = conversation_service.analyze_conversation(conversation_data)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing conversation: {str(e)}"
        )


@app.post("/analyze/batch", response_model=List[ConversationResponse])
async def analyze_conversations_batch(conversations: List[ConversationData]):
    """
    Analyze multiple conversations in batch and return performance metrics for each
    
    Args:
        conversations: List of conversation data to analyze
        
    Returns:
        List of ConversationResponse objects with performance metrics
        
    Raises:
        HTTPException: If there's an error processing the conversation data
    """
    try:
        results = []
        for i, conversation_data in enumerate(conversations):
            try:
                result = conversation_service.analyze_conversation(conversation_data)
                results.append(result)
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Error analyzing conversation at index {i}: {str(e)}"
                )
        
        return results
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing batch analysis: {str(e)}"
        )


@app.get("/metrics/summary")
async def get_metrics_summary():
    """
    Get summary of available performance metrics
    
    Returns:
        Dictionary describing available metrics and their meanings
    """
    return {
        "available_metrics": {
            "response_time_minutes": "Average response time from customer to service provider in minutes",
            "sentiment_score": "Numerical sentiment score (-1.0 to 1.0)",
            "resolution_status": "Status of conversation resolution (Resolved, Pending, In Progress, Unresolved)",
            "customer_satisfaction": "Estimated customer satisfaction level (High, Medium, Low)",
            "interaction_count": "Total number of interactions in the conversation",
            "escalation_required": "Boolean indicating if escalation is recommended"
        },
        "sentiment_mapping": {
            "Positive": 1.0,
            "Neutral": 0.0,
            "Negative": -1.0
        },
        "resolution_statuses": [
            "Resolved",
            "Pending", 
            "In Progress",
            "Unresolved"
        ],
        "satisfaction_levels": [
            "High",
            "Medium",
            "Low"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
