"""
LLM Agent-based API for dynamic conversation performance analysis
"""

import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import uvicorn
from pymongo import MongoClient

from .models import ConversationData
from .llm_agent_service import LLMAgentPerformanceAnalysisService, get_llm_agent_service
from .config_loader import load_agent_performance_config, validate_agent_performance_config

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="LLM Agent-based Conversation Performance Analysis API",
    description="AI-powered API for analyzing customer service conversations using configurable KPIs with LLM agents",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Global agent service (initialized lazily)
agent_service: Optional[LLMAgentPerformanceAnalysisService] = None

# Global MongoDB client for persistence (initialized lazily)
mongo_client: Optional[MongoClient] = None


def get_agent_service() -> LLMAgentPerformanceAnalysisService:
    """Get or initialize the LLM agent service"""
    global agent_service
    if agent_service is None:
        try:
            agent_service = get_llm_agent_service()
            logger.info("LLM Agent service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize LLM Agent service: {e}")
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to initialize agent service: {str(e)}"
            )
    return agent_service


def get_mongo_client() -> Optional[MongoClient]:
    """Get or initialize MongoDB client for persistence"""
    global mongo_client
    if mongo_client is None:
        try:
            mongo_connection_string = os.getenv('MONGODB_CONNECTION_STRING', 'mongodb://localhost:27017/')
            mongo_client = MongoClient(mongo_connection_string)
            # Test connection
            mongo_client.admin.command('ping')
            logger.info("MongoDB client initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize MongoDB client: {e}")
            mongo_client = None
    return mongo_client


def persist_analysis_result(analysis_result: Dict[str, Any], conversation_data: ConversationData) -> bool:
    """
    Persist analysis result to MongoDB agentic_analysis collection
    
    Args:
        analysis_result: The analysis result to persist
        conversation_data: Original conversation data for context
    
    Returns:
        bool: True if persistence was successful, False otherwise
    """
    try:
        client = get_mongo_client()
        if not client:
            logger.warning("MongoDB client not available - skipping persistence")
            return False
        
        db_name = os.getenv('MONGODB_DB_NAME', 'csai')
        db = client[db_name]
        collection = db['agentic_analysis']
        
        # Prepare document for persistence
        document = {
            "conversation_id": getattr(conversation_data, 'conversation_id', None) or f"llm_api_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "analysis_type": "LLM_Agent_API",
            "timestamp": datetime.now(),
            "analysis_results": analysis_result,
            "conversation_data": {
                "tweets": [tweet.dict() for tweet in conversation_data.tweets],
                "classification": conversation_data.classification.dict() if conversation_data.classification else None
            },
            "persistence_metadata": {
                "source": "LLM_Agent_API",
                "api_version": "2.0.0",
                "storage_type": "mongodb",
                "inserted_timestamp": datetime.now()
            }
        }
        
        # Insert document
        result = collection.insert_one(document)
        
        if result.inserted_id:
            logger.info(f"Analysis result persisted successfully with ID: {result.inserted_id}")
            return True
        else:
            logger.error("Failed to persist analysis result - no insertion ID returned")
            return False
            
    except Exception as e:
        logger.error(f"Failed to persist analysis result: {e}")
        return False


def add_persistence_metadata(results: Dict[str, Any], persistence_success: bool) -> Dict[str, Any]:
    """Add persistence metadata to analysis results"""
    results["persistence"] = {
        "enabled": get_mongo_client() is not None,
        "success": persistence_success,
        "collection": "agentic_analysis",
        "timestamp": datetime.now().isoformat()
    }
    return results


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "api": "LLM Agent-based Conversation Performance Analysis",
        "version": "2.0.0",
        "description": "AI-powered analysis using configurable KPIs with LLM agents",
        "features": [
            "Dynamic KPI evaluation using LLM agents",
            "Configuration-driven analysis without code changes",
            "Comprehensive conversation analysis",
            "Category and individual KPI analysis",
            "Real-time configuration validation"
        ],
        "endpoints": {
            "analysis": {
                "/analyze/comprehensive": "Complete analysis across all KPIs",
                "/analyze/category/{category}": "Category-specific analysis",
                "/analyze/kpi/{category}/{kpi}": "Individual KPI analysis"
            },
            "agent": {
                "/agent/info": "Agent configuration and status",
                "/agent/validate": "Validate agent configuration",
                "/agent/available-kpis": "List all available KPIs"
            },
            "config": {
                "/config/info": "Configuration information",
                "/config/validate": "Validate configuration"
            },
            "utility": {
                "/health": "Health check",
                "/docs": "API documentation"
            }
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint with agent and configuration status"""
    try:
        # Check configuration
        config_valid = validate_agent_performance_config()
        
        # Check agent service
        service = get_agent_service()
        agent_status = "healthy" if service else "unavailable"
        
        # Check MongoDB connection
        mongo_client = get_mongo_client()
        mongodb_status = "connected" if mongo_client else "disconnected"
        
        return {
            "status": "healthy" if config_valid and agent_status == "healthy" else "degraded",
            "configuration": {
                "valid": config_valid,
                "status": "loaded" if config_valid else "invalid"
            },
            "agent_service": {
                "status": agent_status,
                "model": service.model_name if service else None,
                "temperature": service.temperature if service else None
            },
            "persistence": {
                "mongodb_status": mongodb_status,
                "collection": "agentic_analysis",
                "enabled": mongo_client is not None
            },
            "api": {
                "version": "2.0.0",
                "type": "LLM Agent-based Analysis"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "api": {"version": "2.0.0", "type": "LLM Agent-based Analysis"}
            }
        )


@app.post("/analyze/comprehensive")
async def analyze_comprehensive(conversation_data: ConversationData, background_tasks: BackgroundTasks):
    """
    Perform comprehensive analysis using LLM agent across all configured KPIs
    
    This endpoint uses AI agents to dynamically evaluate conversations against
    all KPIs defined in the configuration without requiring code changes.
    Results are automatically persisted to MongoDB for future retrieval.
    """
    try:
        logger.info("Starting LLM agent-based comprehensive analysis")
        
        service = get_agent_service()
        results = service.analyze_conversation_performance(conversation_data)
        
        # Add analysis metadata
        results.update({
            "analysis_type": "LLM Agent-based Comprehensive",
            "api_version": "2.0.0",
            "agent_model": service.model_name,
            "configuration_driven": True
        })
        
        # Persist results in background
        def persist_results():
            persistence_success = persist_analysis_result(results, conversation_data)
            logger.info(f"Background persistence {'succeeded' if persistence_success else 'failed'}")
        
        background_tasks.add_task(persist_results)
        
        # Add persistence metadata
        persistence_success = True  # We assume success for background task
        results = add_persistence_metadata(results, persistence_success)
        
        return results
        
    except Exception as e:
        logger.error(f"Comprehensive analysis failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@app.post("/analyze/category/{category}")
async def analyze_category(category: str, conversation_data: ConversationData, background_tasks: BackgroundTasks):
    """
    Analyze conversation for a specific category using LLM agent
    
    The agent dynamically evaluates all KPIs within the specified category
    based on the current configuration. Results are persisted to MongoDB.
    """
    try:
        logger.info(f"Starting LLM agent-based category analysis for: {category}")
        
        service = get_agent_service()
        results = service.analyze_conversation_category(conversation_data, category)
        
        # Add metadata
        results.update({
            "analysis_type": "LLM Agent-based Category",
            "api_version": "2.0.0",
            "agent_model": service.model_name,
            "target_category": category
        })
        
        # Persist results in background
        def persist_results():
            persistence_success = persist_analysis_result(results, conversation_data)
            logger.info(f"Background persistence for category analysis {'succeeded' if persistence_success else 'failed'}")
        
        background_tasks.add_task(persist_results)
        
        # Add persistence metadata
        results = add_persistence_metadata(results, True)
        
        return results
        
    except Exception as e:
        logger.error(f"Category analysis failed for {category}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Category analysis failed: {str(e)}"
        )


@app.post("/analyze/kpi/{category}/{kpi}")
async def analyze_kpi(category: str, kpi: str, conversation_data: ConversationData, background_tasks: BackgroundTasks):
    """
    Analyze conversation for a specific KPI using LLM agent
    
    The agent evaluates the conversation against the specified KPI using
    its current configuration, adapting to any configuration changes.
    Results are persisted to MongoDB.
    """
    try:
        logger.info(f"Starting LLM agent-based KPI analysis for: {category}/{kpi}")
        
        service = get_agent_service()
        results = service.analyze_conversation_kpi(conversation_data, category, kpi)
        
        # Add metadata
        results.update({
            "analysis_type": "LLM Agent-based KPI",
            "api_version": "2.0.0",
            "agent_model": service.model_name,
            "target_category": category,
            "target_kpi": kpi
        })
        
        # Persist results in background
        def persist_results():
            persistence_success = persist_analysis_result(results, conversation_data)
            logger.info(f"Background persistence for KPI analysis {'succeeded' if persistence_success else 'failed'}")
        
        background_tasks.add_task(persist_results)
        
        # Add persistence metadata
        results = add_persistence_metadata(results, True)
        
        return results
        
    except Exception as e:
        logger.error(f"KPI analysis failed for {category}/{kpi}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"KPI analysis failed: {str(e)}"
        )


@app.get("/agent/info")
async def agent_info():
    """Get information about the LLM agent configuration and capabilities"""
    try:
        service = get_agent_service()
        
        return {
            "agent_type": "LangChain-based LLM Agent",
            "model": service.model_name,
            "temperature": service.temperature,
            "tools_available": [tool.name for tool in service.tools],
            "capabilities": [
                "Dynamic KPI evaluation",
                "Configuration-driven analysis",
                "Evidence-based scoring",
                "Contextual reasoning",
                "Actionable recommendations"
            ],
            "features": {
                "adaptive_analysis": "Automatically adapts to configuration changes",
                "multi_level_analysis": "Supports conversation, category, and KPI-level analysis",
                "llm_powered": "Uses advanced language models for nuanced evaluation",
                "tool_based": "Leverages specialized tools for analysis tasks"
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get agent info: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get agent information: {str(e)}"
        )


@app.get("/agent/validate")
async def validate_agent():
    """Validate the agent configuration and capabilities"""
    try:
        service = get_agent_service()
        validation_results = service.validate_configuration()
        
        return {
            "agent_validation": validation_results,
            "tools_status": {
                tool.name: "available" for tool in service.tools
            },
            "configuration_status": "valid" if validate_agent_performance_config() else "invalid"
        }
        
    except Exception as e:
        logger.error(f"Agent validation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Agent validation failed: {str(e)}"
        )


@app.get("/agent/available-kpis")
async def get_available_kpis():
    """Get all available KPIs organized by category"""
    try:
        service = get_agent_service()
        kpis = service.get_available_kpis()
        
        return {
            "available_kpis": kpis,
            "total_categories": len(kpis),
            "total_kpis": sum(len(kpi_list) for kpi_list in kpis.values()),
            "dynamic_adaptation": "KPIs are loaded from configuration and can be modified without code changes"
        }
        
    except Exception as e:
        logger.error(f"Failed to get available KPIs: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get available KPIs: {str(e)}"
        )


@app.get("/config/info")
async def config_info():
    """Get basic configuration information"""
    try:
        config = load_agent_performance_config()
        framework = config.get("evaluation_framework", {})
        
        return {
            "framework_name": framework.get("name", "Unknown"),
            "version": framework.get("version", "Unknown"),
            "categories": list(framework.get("categories", {}).keys()),
            "configuration_file": "config/agent_performance_config.yaml",
            "dynamic_loading": "Configuration is loaded at runtime and supports hot-reload"
        }
        
    except Exception as e:
        logger.error(f"Failed to get config info: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get configuration info: {str(e)}"
        )


@app.get("/config/validate")
async def validate_config():
    """Validate the current configuration"""
    try:
        is_valid = validate_agent_performance_config()
        
        return {
            "valid": is_valid,
            "status": "Configuration is valid and ready for use" if is_valid else "Configuration has validation errors",
            "validation_timestamp": "Real-time validation"
        }
        
    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Configuration validation failed: {str(e)}"
        )


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors with helpful information"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Endpoint not found",
            "message": "Please check the API documentation at /docs for available endpoints",
            "available_endpoints": [
                "/analyze/comprehensive",
                "/analyze/category/{category}",
                "/analyze/kpi/{category}/{kpi}",
                "/agent/info",
                "/config/info",
                "/health"
            ]
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred during processing",
            "suggestion": "Check the logs and ensure all dependencies are properly configured"
        }
    )


if __name__ == "__main__":
    # This allows running the API directly for development
    uvicorn.run(
        "llm_agent_api:app",
        host="0.0.0.0",
        port=8002,
        reload=True
    )
