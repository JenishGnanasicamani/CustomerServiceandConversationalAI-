"""
Enhanced API endpoints for comprehensive agent performance evaluation
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from .models import ConversationData, ConversationResponse
from .enhanced_service import enhanced_service
from .config_loader import config_loader, validate_agent_performance_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Enhanced Agent Performance Analysis API",
    description="Comprehensive agent performance evaluation using configurable KPIs",
    version="2.0.0"
)


@app.on_event("startup")
async def startup_event():
    """Initialize the API and validate configuration on startup"""
    try:
        # Validate configuration
        if validate_agent_performance_config():
            logger.info("Configuration validated successfully")
        else:
            logger.error("Configuration validation failed")
            raise Exception("Invalid configuration")
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Enhanced Agent Performance Analysis API",
        "version": "2.0.0",
        "description": "Comprehensive agent performance evaluation with configurable KPIs",
        "endpoints": {
            "analyze_comprehensive": "/analyze/comprehensive",
            "analyze_category": "/analyze/category/{category}",
            "config_info": "/config/info",
            "config_categories": "/config/categories",
            "config_kpi": "/config/kpi/{category}/{kpi}",
            "health": "/health"
        }
    }


@app.post("/analyze/comprehensive", response_model=Dict[str, Any])
async def analyze_conversation_comprehensive(conversation_data: ConversationData):
    """
    Perform comprehensive analysis across all configured categories and KPIs
    
    Args:
        conversation_data: Input conversation data
        
    Returns:
        Comprehensive analysis results with all KPIs and categories
    """
    try:
        logger.info(f"Starting comprehensive analysis for conversation")
        
        # Perform comprehensive analysis
        results = enhanced_service.analyze_conversation_comprehensive(conversation_data)
        
        logger.info(f"Comprehensive analysis completed successfully")
        return results
        
    except Exception as e:
        logger.error(f"Error in comprehensive analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/analyze/category/{category}")
async def analyze_conversation_category(category: str, conversation_data: ConversationData):
    """
    Analyze conversation for a specific category only
    
    Args:
        category: Category name (accuracy_compliance, empathy_communication, efficiency_resolution)
        conversation_data: Input conversation data
        
    Returns:
        Analysis results for the specified category
    """
    try:
        logger.info(f"Starting category analysis for: {category}")
        
        # Validate category exists
        available_categories = config_loader.get_all_categories()
        if category not in available_categories:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid category. Available categories: {available_categories}"
            )
        
        # Perform category-specific analysis
        category_result = enhanced_service._analyze_category(conversation_data, category)
        
        results = {
            "conversation_id": getattr(conversation_data, 'conversation_number', None) or getattr(conversation_data, 'conversation_id', 'unknown'),
            "analysis_timestamp": datetime.now().isoformat(),
            "category": category_result
        }
        
        logger.info(f"Category analysis completed successfully for: {category}")
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in category analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Category analysis failed: {str(e)}")


@app.post("/analyze/kpi/{category}/{kpi}")
async def analyze_conversation_kpi(category: str, kpi: str, conversation_data: ConversationData):
    """
    Analyze conversation for a specific KPI only
    
    Args:
        category: Category name
        kpi: KPI name
        conversation_data: Input conversation data
        
    Returns:
        Analysis results for the specified KPI
    """
    try:
        logger.info(f"Starting KPI analysis for: {category}/{kpi}")
        
        # Get KPI configuration
        kpi_config = config_loader.get_kpi_config(category, kpi)
        if not kpi_config:
            raise HTTPException(
                status_code=404, 
                detail=f"KPI '{kpi}' not found in category '{category}'"
            )
        
        # Perform KPI-specific analysis
        kpi_result = enhanced_service._analyze_kpi(conversation_data, kpi, kpi_config, category)
        
        results = {
            "conversation_id": getattr(conversation_data, 'conversation_id', 'unknown'),
            "analysis_timestamp": datetime.now().isoformat(),
            "category": category,
            "kpi": kpi_result
        }
        
        logger.info(f"KPI analysis completed successfully for: {category}/{kpi}")
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in KPI analysis: {e}")
        raise HTTPException(status_code=500, detail=f"KPI analysis failed: {str(e)}")


@app.get("/config/info")
async def get_config_info():
    """
    Get basic information about the configuration
    
    Returns:
        Configuration framework information
    """
    try:
        config_data = config_loader.load_config()
        framework_info = config_data.get('evaluation_framework', {})
        
        return {
            "framework_name": framework_info.get('name', 'Unknown'),
            "framework_version": framework_info.get('version', 'Unknown'),
            "total_categories": len(framework_info.get('categories', {})),
            "categories": list(framework_info.get('categories', {}).keys()),
            "settings": config_data.get('settings', {})
        }
        
    except Exception as e:
        logger.error(f"Error getting config info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get config info: {str(e)}")


@app.get("/config/categories")
async def get_config_categories():
    """
    Get detailed information about all configured categories
    
    Returns:
        Detailed information about all categories and their KPIs
    """
    try:
        config_data = config_loader.load_config()
        categories = config_data.get('evaluation_framework', {}).get('categories', {})
        
        result = {}
        for category_key, category_data in categories.items():
            result[category_key] = {
                "name": category_data.get('name', ''),
                "description": category_data.get('description', ''),
                "kpi_count": len(category_data.get('kpis', {})),
                "kpis": list(category_data.get('kpis', {}).keys())
            }
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get categories: {str(e)}")


@app.get("/config/kpi/{category}/{kpi}")
async def get_kpi_config(category: str, kpi: str):
    """
    Get detailed configuration for a specific KPI
    
    Args:
        category: Category name
        kpi: KPI name
        
    Returns:
        Detailed KPI configuration
    """
    try:
        kpi_config = config_loader.get_kpi_config(category, kpi)
        if not kpi_config:
            raise HTTPException(
                status_code=404, 
                detail=f"KPI '{kpi}' not found in category '{category}'"
            )
        
        return kpi_config.dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting KPI config: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get KPI config: {str(e)}")


@app.get("/config/validate")
async def validate_configuration():
    """
    Validate the current configuration
    
    Returns:
        Validation results
    """
    try:
        is_valid = validate_agent_performance_config()
        
        return {
            "valid": is_valid,
            "timestamp": datetime.now().isoformat(),
            "message": "Configuration is valid" if is_valid else "Configuration validation failed"
        }
        
    except Exception as e:
        logger.error(f"Error validating config: {e}")
        return {
            "valid": False,
            "timestamp": datetime.now().isoformat(),
            "message": f"Validation error: {str(e)}"
        }


@app.get("/analyze/benchmark")
async def get_performance_benchmarks():
    """
    Get performance benchmarks and targets for all KPIs
    
    Returns:
        Benchmark information for all configured KPIs
    """
    try:
        benchmarks = {}
        
        for category in config_loader.get_all_categories():
            category_kpis = config_loader.get_category_kpis(category)
            benchmarks[category] = {}
            
            for kpi_name, kpi_config in category_kpis.items():
                benchmarks[category][kpi_name] = {
                    "name": kpi_config.name,
                    "description": kpi_config.description,
                    "scale": {
                        "type": kpi_config.scale.type,
                        "range": kpi_config.scale.range,
                        "description": kpi_config.scale.description
                    },
                    "target": {
                        "value": kpi_config.target.value,
                        "operator": kpi_config.target.operator,
                        "description": kpi_config.target.description
                    },
                    "interpretation": kpi_config.interpretation if kpi_config.interpretation else None
                }
        
        return benchmarks
        
    except Exception as e:
        logger.error(f"Error getting benchmarks: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get benchmarks: {str(e)}")


@app.get("/health")
async def health_check():
    """
    Health check endpoint
    
    Returns:
        API health status
    """
    try:
        # Check if configuration is valid
        config_valid = validate_agent_performance_config()
        
        # Check if service is initialized
        service_ready = hasattr(enhanced_service, 'config')
        
        status = "healthy" if config_valid and service_ready else "unhealthy"
        
        return {
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "config_valid": config_valid,
            "service_ready": service_ready,
            "version": "2.0.0"
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "version": "2.0.0"
        }


# Exception handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.now().isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("enhanced_api:app", host="0.0.0.0", port=8001, reload=True)
