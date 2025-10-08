#!/usr/bin/env python3
"""
Reporting API for Customer Conversation Performance Analysis
FastAPI endpoints for generating performance reports with LLM summaries
"""

import os
import sys
from datetime import datetime, date
from pathlib import Path
from typing import Optional, Dict, Any
import logging

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# Add src directory to Python path
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir))

try:
    from .reporting_service import ReportingService
except ImportError:
    from reporting_service import ReportingService

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Customer Conversation Performance Reporting API",
    description="API for generating performance reports with LLM-powered insights",
    version="1.0.0"
)

# Global reporting service instance
reporting_service = None

class ReportRequest(BaseModel):
    """Request model for performance reports"""
    start_date: str = Field(..., description="Start date in YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS format")
    end_date: str = Field(..., description="End date in YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS format")
    customer: Optional[str] = Field(None, description="Optional customer filter (use 'all' or omit for all customers)")

class ReportResponse(BaseModel):
    """Response model for performance reports"""
    status: str
    message: Optional[str] = None
    query_parameters: Dict[str, Any]
    selected_records: list
    summary: Dict[str, list]
    aggregated_insights: Optional[Dict[str, Any]] = None
    report_metadata: Dict[str, Any]

class DataSourceConfigRequest(BaseModel):
    """Request model for data source configuration"""
    source_type: str = Field(..., description="Type of data source: 'mongodb' or 'file'")
    collection_name: Optional[str] = Field("agentic_analysis", description="MongoDB collection name (for mongodb source)")
    file_path: Optional[str] = Field(None, description="File path or folder path (for file source)")

class DataSourceConfigResponse(BaseModel):
    """Response model for data source configuration"""
    status: str
    message: str
    current_config: Dict[str, Any]

def get_reporting_service():
    """Dependency to get reporting service instance"""
    global reporting_service
    if reporting_service is None:
        # Get MongoDB connection from environment variable
        mongo_connection_string = os.getenv('MONGODB_CONNECTION_STRING', 'mongodb://localhost:27017/')
        db_name = os.getenv('MONGODB_DB_NAME', 'csai')
        
        reporting_service = ReportingService(mongo_connection_string, db_name)
        
        # Connect to MongoDB
        if not reporting_service.connect_to_mongodb():
            raise HTTPException(status_code=500, detail="Failed to connect to MongoDB")
    
    return reporting_service

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Customer Conversation Performance Reporting API",
        "version": "1.0.0",
        "description": "Generate performance reports with LLM-powered insights",
        "endpoints": {
            "POST /reports/generate": "Generate performance report by date range and customer",
            "GET /reports/generate": "Generate performance report using query parameters",
            "POST /config/datasource": "Configure data source for sentiment analysis data",
            "GET /config/datasource": "Get current data source configuration",
            "GET /health": "Health check endpoint",
            "GET /docs": "API documentation"
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        service = get_reporting_service()
        return {
            "status": "healthy",
            "database_connected": service.client is not None,
            "llm_service_available": service.llm_service is not None,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

@app.post("/reports/generate", response_model=ReportResponse)
async def generate_report_post(
    request: ReportRequest,
    service: ReportingService = Depends(get_reporting_service)
):
    """
    Generate performance report using POST request with JSON body
    
    Args:
        request: Report request with start_date, end_date, and optional customer
        
    Returns:
        Performance report with selected records and LLM summary
    """
    try:
        logger.info(f"Generating report for: {request.start_date} to {request.end_date}, customer: {request.customer}")
        
        # Generate report
        report = service.generate_performance_report(
            start_date=request.start_date,
            end_date=request.end_date,
            customer=request.customer
        )
        
        return report
        
    except Exception as e:
        logger.error(f"Failed to generate report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/reports/generate", response_model=ReportResponse)
async def generate_report_get(
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    customer: Optional[str] = Query(None, description="Optional customer filter"),
    service: ReportingService = Depends(get_reporting_service)
):
    """
    Generate performance report using GET request with query parameters
    
    Args:
        start_date: Start date for the report
        end_date: End date for the report
        customer: Optional customer filter
        
    Returns:
        Performance report with selected records and LLM summary
    """
    try:
        logger.info(f"Generating report for: {start_date} to {end_date}, customer: {customer}")
        
        # Generate report
        report = service.generate_performance_report(
            start_date=start_date,
            end_date=end_date,
            customer=customer
        )
        
        return report
        
    except Exception as e:
        logger.error(f"Failed to generate report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/reports/sample")
async def get_sample_report():
    """
    Get a sample report structure for reference
    """
    return {
        "description": "Sample report structure",
        "sample_request": {
            "start_date": "2023-01-01",
            "end_date": "2023-01-31",
            "customer": "customer_123"
        },
        "sample_response": {
            "status": "success",
            "query_parameters": {
                "start_date": "2023-01-01",
                "end_date": "2023-01-31",
                "customer": "customer_123",
                "records_found": 5
            },
            "selected_records": [
                {
                    "conversation_id": "conv_507f1f77bcf86cd799439011",
                    "customer": "customer_123",
                    "created_at": "2023-01-15T14:30:00Z",
                    "created_time": "14:30:00",
                    "conversation_summary": {
                        "final_sentiment": "Positive",
                        "intent": "Technical Support",
                        "topic": "Account Issues"
                    },
                    "performance_metrics": {
                        "empathy_communication": {
                            "empathy_score": 8.5
                        }
                    }
                }
            ],
            "summary": {
                "what_went_well": [
                    "High positive sentiment rate (80.0%)",
                    "Strong empathy scores in customer interactions"
                ],
                "what_needs_improvement": [
                    "Response time could be improved"
                ],
                "training_needs": [
                    "Advanced technical troubleshooting training"
                ]
            },
            "aggregated_insights": {
                "total_conversations": 5,
                "unique_customers": 3,
                "sentiment_distribution": {
                    "Positive": 4,
                    "Neutral": 1
                },
                "intent_distribution": {
                    "Technical Support": 3,
                    "Billing Inquiry": 2
                },
                "topic_distribution": {
                    "Account Issues": 2,
                    "Payment": 2,
                    "Technical": 1
                }
            },
            "report_metadata": {
                "generated_at": "2023-01-31T12:00:00Z",
                "analysis_method": "claude-4",
                "total_records": 5
            }
        }
    }

@app.get("/reports/stats")
async def get_collection_stats(
    service: ReportingService = Depends(get_reporting_service)
):
    """
    Get basic statistics about the agentic_analysis collection
    """
    try:
        # Get collection stats
        total_records = service.agentic_collection.count_documents({})
        
        # Get date range of records
        earliest_record = service.agentic_collection.find_one(
            {}, 
            sort=[("created_at", 1)]
        )
        latest_record = service.agentic_collection.find_one(
            {}, 
            sort=[("created_at", -1)]
        )
        
        # Get unique customers count
        unique_customers = len(service.agentic_collection.distinct("customer"))
        
        # Get recent records count (last 30 days)
        from datetime import timedelta
        thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
        recent_records = service.agentic_collection.count_documents({
            "created_at": {"$gte": thirty_days_ago}
        })
        
        return {
            "collection_name": "agentic_analysis",
            "total_records": total_records,
            "unique_customers": unique_customers,
            "recent_records_30_days": recent_records,
            "date_range": {
                "earliest_record": earliest_record.get("created_at") if earliest_record else None,
                "latest_record": latest_record.get("created_at") if latest_record else None
            },
            "sample_customers": service.agentic_collection.distinct("customer")[:10] if total_records > 0 else [],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get collection stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/config/datasource", response_model=DataSourceConfigResponse)
async def configure_data_source(
    request: DataSourceConfigRequest,
    service: ReportingService = Depends(get_reporting_service)
):
    """
    Configure the data source for sentiment analysis data
    
    Args:
        request: Data source configuration request
        
    Returns:
        Configuration status and current config
    """
    try:
        logger.info(f"Configuring data source: {request.source_type}, collection: {request.collection_name}, file_path: {request.file_path}")
        
        # Validate source type
        if request.source_type not in ["mongodb", "file"]:
            raise HTTPException(
                status_code=400, 
                detail="Invalid source_type. Must be 'mongodb' or 'file'"
            )
        
        # Validate required parameters
        if request.source_type == "file" and not request.file_path:
            raise HTTPException(
                status_code=400,
                detail="file_path is required when source_type is 'file'"
            )
        
        # Configure the data source
        success = service.configure_data_source(
            source_type=request.source_type,
            collection_name=request.collection_name or "agentic_analysis",
            file_path=request.file_path
        )
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to configure data source"
            )
        
        # Get current configuration
        current_config = service.get_data_source_config()
        
        return DataSourceConfigResponse(
            status="success",
            message=f"Data source configured successfully to {request.source_type}",
            current_config=current_config
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to configure data source: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/config/datasource", response_model=DataSourceConfigResponse)
async def get_data_source_config(
    service: ReportingService = Depends(get_reporting_service)
):
    """
    Get current data source configuration
    
    Returns:
        Current data source configuration
    """
    try:
        current_config = service.get_data_source_config()
        
        return DataSourceConfigResponse(
            status="success",
            message="Current data source configuration retrieved",
            current_config=current_config
        )
        
    except Exception as e:
        logger.error(f"Failed to get data source config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global reporting_service
    if reporting_service:
        reporting_service.cleanup()

if __name__ == "__main__":
    # Get configuration from environment variables
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8003"))
    
    # Run the API server
    uvicorn.run(
        "reporting_api:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
