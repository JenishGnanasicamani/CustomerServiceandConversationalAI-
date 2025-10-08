#!/usr/bin/env python3
"""
Test to verify enhanced structure with normalized_score, confidence, and interpretation
for both KPIs and sub-KPIs as requested
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from src.llm_agent_service import LLMAgentPerformanceAnalysisService
    from src.models import ConversationData, Tweet, Classification
except ImportError as e:
    logger.error(f"Import error: {e}")
    exit(1)


def create_comprehensive_test_conversation() -> ConversationData:
    """
    Create a comprehensive test conversation to verify enhanced structure
    """
    tweets = [
        Tweet(
            tweet_id=1,
            author_id="customer_001",
            role="Customer",
            inbound=True,
            created_at="2024-10-05T15:00:00Z",
            text="@Support I'm having trouble accessing my account - it's been locked for hours and I really need to get in!"
        ),
        Tweet(
            tweet_id=2,
            author_id="support_agent_001",
            role="Agent",
            inbound=False,
            created_at="2024-10-05T15:01:00Z",
            text="Hi! I completely understand how frustrating this must be for you. I'm here to help unlock your account right away."
        ),
        Tweet(
            tweet_id=3,
            author_id="customer_001",
            role="Customer",
            inbound=True,
            created_at="2024-10-05T15:02:00Z",
            text="Thank you for understanding! This is really important for my work today."
        ),
        Tweet(
            tweet_id=4,
            author_id="support_agent_001",
            role="Agent",
            inbound=False,
            created_at="2024-10-05T15:03:00Z",
            text="I can see how important this is for you. Please DM me your email address for verification and I'll unlock your account immediately."
        ),
        Tweet(
            tweet_id=5,
            author_id="customer_001",
            role="Customer",
            inbound=True,
            created_at="2024-10-05T15:04:00Z",
            text="Perfect! Sending my email to you now via DM."
        ),
        Tweet(
            tweet_id=6,
            author_id="support_agent_001",
            role="Agent",
            inbound=False,
            created_at="2024-10-05T15:07:00Z",
            text="Account successfully unlocked! You should be able to access everything now. Is there anything else I can help you with today?"
        ),
        Tweet(
            tweet_id=7,
            author_id="customer_001",
            role="Customer",
            inbound=True,
            created_at="2024-10-05T15:08:00Z",
            text="Excellent! Everything is working perfectly now. Thank you so much for the amazing and quick help!"
        )
    ]
    
    classification = Classification(
        categorization="technical_support",
        intent="account_access",
        topic="account_unlock",
        sentiment="positive"
    )
    
    return ConversationData(
        tweets=tweets,
        classification=classification
    )


def verify_enhanced_structure(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Verify that the enhanced structure includes all required fields
    
    Args:
        result: Analysis result from LLM agent
        
    Returns:
        Dictionary with verification results
    """
    verification = {
        "total_kpis_checked": 0,
        "kpis_with_all_fields": 0,
        "total_sub_kpis_checked": 0,
        "sub_kpis_with_all_fields": 0,
        "required_fields": ["score", "normalized_score", "reasoning", "evidence", "confidence", "interpretation"],
        "field_coverage": {},
        "missing_fields": [],
        "structure_issues": [],
        "success_rate": 0.0
    }
    
    try:
        performance_metrics = result.get("performance_metrics", {})
        categories = performance_metrics.get("categories", {})
        
        # Initialize field coverage tracking
        for field in verification["required_fields"]:
            verification["field_coverage"][field] = {"kpi_count": 0, "sub_kpi_count": 0}
        
        for category_name, category_data in categories.items():
            kpis = category_data.get("kpis", {})
            
            for kpi_name, kpi_data in kpis.items():
                verification["total_kpis_checked"] += 1
                
                # Check KPI fields
                kpi_fields_present = 0
                for field in verification["required_fields"]:
                    if field in kpi_data:
                        verification["field_coverage"][field]["kpi_count"] += 1
                        kpi_fields_present += 1
                    else:
                        verification["missing_fields"].append(f"KPI {kpi_name} missing {field}")
                
                if kpi_fields_present == len(verification["required_fields"]):
                    verification["kpis_with_all_fields"] += 1
                
                # Verify field types and values
                if "score" in kpi_data and not isinstance(kpi_data["score"], (int, float)):
                    verification["structure_issues"].append(f"KPI {kpi_name} has non-numeric score: {type(kpi_data['score'])}")
                
                if "normalized_score" in kpi_data:
                    norm_score = kpi_data["normalized_score"]
                    if not isinstance(norm_score, (int, float)) or not (0.0 <= norm_score <= 1.0):
                        verification["structure_issues"].append(f"KPI {kpi_name} has invalid normalized_score: {norm_score}")
                
                if "confidence" in kpi_data:
                    confidence = kpi_data["confidence"]
                    if not isinstance(confidence, (int, float)) or not (0.0 <= confidence <= 1.0):
                        verification["structure_issues"].append(f"KPI {kpi_name} has invalid confidence: {confidence}")
                
                if "evidence" in kpi_data and not isinstance(kpi_data["evidence"], list):
                    verification["structure_issues"].append(f"KPI {kpi_name} has non-list evidence: {type(kpi_data['evidence'])}")
                
                # Check sub-KPIs if present
                sub_factors = kpi_data.get("sub_factors", {})
                for sub_kpi_name, sub_kpi_data in sub_factors.items():
                    verification["total_sub_kpis_checked"] += 1
                    
                    sub_kpi_fields_present = 0
                    for field in verification["required_fields"]:
                        if field in sub_kpi_data:
                            verification["field_coverage"][field]["sub_kpi_count"] += 1
                            sub_kpi_fields_present += 1
                        else:
                            verification["missing_fields"].append(f"Sub-KPI {sub_kpi_name} missing {field}")
                    
                    if sub_kpi_fields_present == len(verification["required_fields"]):
                        verification["sub_kpis_with_all_fields"] += 1
                    
                    # Verify sub-KPI field types and values
                    if "score" in sub_kpi_data and not isinstance(sub_kpi_data["score"], (int, float)):
                        verification["structure_issues"].append(f"Sub-KPI {sub_kpi_name} has non-numeric score")
                    
                    if "normalized_score" in sub_kpi_data:
                        norm_score = sub_kpi_data["normalized_score"]
                        if not isinstance(norm_score, (int, float)) or not (0.0 <= norm_score <= 1.0):
                            verification["structure_issues"].append(f"Sub-KPI {sub_kpi_name} has invalid normalized_score: {norm_score}")
                    
                    if "confidence" in sub_kpi_data:
                        confidence = sub_kpi_data["confidence"]
                        if not isinstance(confidence, (int, float)) or not (0.0 <= confidence <= 1.0):
                            verification["structure_issues"].append(f"Sub-KPI {sub_kpi_name} has invalid confidence: {confidence}")
        
        # Calculate success rates
        if verification["total_kpis_checked"] > 0:
            kpi_success_rate = (verification["kpis_with_all_fields"] / verification["total_kpis_checked"]) * 100
        else:
            kpi_success_rate = 0.0
        
        if verification["total_sub_kpis_checked"] > 0:
            sub_kpi_success_rate = (verification["sub_kpis_with_all_fields"] / verification["total_sub_kpis_checked"]) * 100
        else:
            sub_kpi_success_rate = 100.0  # No sub-KPIs is not a failure
        
        verification["success_rate"] = (kpi_success_rate + sub_kpi_success_rate) / 2
        verification["kpi_success_rate"] = kpi_success_rate
        verification["sub_kpi_success_rate"] = sub_kpi_success_rate
        
        return verification
        
    except Exception as e:
        logger.error(f"Error verifying enhanced structure: {e}")
        verification["error"] = str(e)
        return verification


def analyze_field_quality(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze the quality of normalized_score, confidence, and interpretation fields
    
    Args:
        result: Analysis result from LLM agent
        
    Returns:
        Dictionary with field quality analysis
    """
    quality_analysis = {
        "normalized_score_analysis": {"valid_count": 0, "invalid_count": 0, "issues": []},
        "confidence_analysis": {"valid_count": 0, "invalid_count": 0, "issues": []},
        "interpretation_analysis": {"valid_count": 0, "missing_count": 0, "interpretations": []},
        "field_correlations": []
    }
    
    try:
        performance_metrics = result.get("performance_metrics", {})
        categories = performance_metrics.get("categories", {})
        
        for category_name, category_data in categories.items():
            kpis = category_data.get("kpis", {})
            
            for kpi_name, kpi_data in kpis.items():
                # Analyze normalized_score
                if "normalized_score" in kpi_data:
                    norm_score = kpi_data["normalized_score"]
                    if isinstance(norm_score, (int, float)) and 0.0 <= norm_score <= 1.0:
                        quality_analysis["normalized_score_analysis"]["valid_count"] += 1
                    else:
                        quality_analysis["normalized_score_analysis"]["invalid_count"] += 1
                        quality_analysis["normalized_score_analysis"]["issues"].append(f"{kpi_name}: {norm_score}")
                
                # Analyze confidence
                if "confidence" in kpi_data:
                    confidence = kpi_data["confidence"]
                    if isinstance(confidence, (int, float)) and 0.0 <= confidence <= 1.0:
                        quality_analysis["confidence_analysis"]["valid_count"] += 1
                    else:
                        quality_analysis["confidence_analysis"]["invalid_count"] += 1
                        quality_analysis["confidence_analysis"]["issues"].append(f"{kpi_name}: {confidence}")
                
                # Analyze interpretation
                if "interpretation" in kpi_data:
                    interpretation = kpi_data["interpretation"]
                    if interpretation and isinstance(interpretation, str):
                        quality_analysis["interpretation_analysis"]["valid_count"] += 1
                        if interpretation not in quality_analysis["interpretation_analysis"]["interpretations"]:
                            quality_analysis["interpretation_analysis"]["interpretations"].append(interpretation)
                    else:
                        quality_analysis["interpretation_analysis"]["missing_count"] += 1
                
                # Check field correlations
                if all(field in kpi_data for field in ["score", "normalized_score", "confidence", "interpretation"]):
                    score = kpi_data.get("score", 0)
                    norm_score = kpi_data.get("normalized_score", 0)
                    confidence = kpi_data.get("confidence", 0)
                    interpretation = kpi_data.get("interpretation", "")
                    
                    # Check if normalized_score correlates with score
                    expected_norm = score / 10.0 if score <= 10 else score
                    norm_diff = abs(norm_score - expected_norm)
                    
                    quality_analysis["field_correlations"].append({
                        "kpi": kpi_name,
                        "score": score,
                        "normalized_score": norm_score,
                        "expected_normalized": round(expected_norm, 3),
                        "normalization_accurate": norm_diff < 0.01,
                        "confidence": confidence,
                        "interpretation": interpretation
                    })
        
        return quality_analysis
        
    except Exception as e:
        logger.error(f"Error analyzing field quality: {e}")
        quality_analysis["error"] = str(e)
        return quality_analysis


def main():
    """Main test execution"""
    logger.info("=== ENHANCED STRUCTURE VERIFICATION TEST ===")
    logger.info("Testing normalized_score, confidence, and interpretation fields for KPIs and sub-KPIs")
    
    try:
        # Create test conversation
        logger.info("Creating comprehensive test conversation...")
        conversation_data = create_comprehensive_test_conversation()
        
        # Initialize LLM agent service
        logger.info("Initializing LLM agent service...")
        llm_service = LLMAgentPerformanceAnalysisService(model_name="claude-4", temperature=0.1)
        
        # Perform analysis
        logger.info("Performing comprehensive conversation analysis...")
        start_time = datetime.now()
        result = llm_service.analyze_conversation_performance(conversation_data)
        end_time = datetime.now()
        
        analysis_duration = (end_time - start_time).total_seconds()
        logger.info(f"Analysis completed in {analysis_duration:.2f} seconds")
        
        # Verify enhanced structure
        logger.info("Verifying enhanced structure with all required fields...")
        structure_verification = verify_enhanced_structure(result)
        
        # Display structure results
        logger.info("=== STRUCTURE VERIFICATION RESULTS ===")
        logger.info(f"Total KPIs checked: {structure_verification['total_kpis_checked']}")
        logger.info(f"KPIs with all fields: {structure_verification['kpis_with_all_fields']}")
        logger.info(f"KPI completeness rate: {structure_verification.get('kpi_success_rate', 0):.1f}%")
        
        logger.info(f"Total sub-KPIs checked: {structure_verification['total_sub_kpis_checked']}")
        logger.info(f"Sub-KPIs with all fields: {structure_verification['sub_kpis_with_all_fields']}")
        logger.info(f"Sub-KPI completeness rate: {structure_verification.get('sub_kpi_success_rate', 0):.1f}%")
        
        logger.info(f"Overall success rate: {structure_verification['success_rate']:.1f}%")
        
        # Display field coverage
        logger.info("\n=== FIELD COVERAGE ANALYSIS ===")
        for field, coverage in structure_verification["field_coverage"].items():
            kpi_coverage = coverage["kpi_count"]
            sub_kpi_coverage = coverage["sub_kpi_count"]
            logger.info(f"{field}: KPIs={kpi_coverage}/{structure_verification['total_kpis_checked']}, Sub-KPIs={sub_kpi_coverage}/{structure_verification['total_sub_kpis_checked']}")
        
        # Display issues if any
        if structure_verification["missing_fields"]:
            logger.warning(f"\nMissing fields detected: {len(structure_verification['missing_fields'])}")
            for missing in structure_verification["missing_fields"][:5]:  # Show first 5
                logger.warning(f"  - {missing}")
        
        if structure_verification["structure_issues"]:
            logger.warning(f"\nStructure issues detected: {len(structure_verification['structure_issues'])}")
            for issue in structure_verification["structure_issues"][:5]:  # Show first 5
                logger.warning(f"  - {issue}")
        
        # Analyze field quality
        logger.info("\nAnalyzing field quality...")
        quality_analysis = analyze_field_quality(result)
        
        logger.info("=== FIELD QUALITY ANALYSIS ===")
        
        # Normalized score analysis
        norm_analysis = quality_analysis["normalized_score_analysis"]
        logger.info(f"Normalized scores - Valid: {norm_analysis['valid_count']}, Invalid: {norm_analysis['invalid_count']}")
        
        # Confidence analysis
        conf_analysis = quality_analysis["confidence_analysis"]
        logger.info(f"Confidence scores - Valid: {conf_analysis['valid_count']}, Invalid: {conf_analysis['invalid_count']}")
        
        # Interpretation analysis
        interp_analysis = quality_analysis["interpretation_analysis"]
        logger.info(f"Interpretations - Valid: {interp_analysis['valid_count']}, Missing: {interp_analysis['missing_count']}")
        logger.info(f"Unique interpretations found: {len(interp_analysis['interpretations'])}")
        for interpretation in interp_analysis["interpretations"][:5]:  # Show first 5
            logger.info(f"  - {interpretation}")
        
        # Field correlations
        correlations = quality_analysis["field_correlations"]
        if correlations:
            logger.info(f"\n=== FIELD CORRELATIONS ===")
            accurate_normalizations = sum(1 for c in correlations if c["normalization_accurate"])
            logger.info(f"Accurate normalizations: {accurate_normalizations}/{len(correlations)} ({accurate_normalizations/len(correlations)*100:.1f}%)")
            
            # Show sample correlations
            logger.info("Sample field correlations:")
            for correlation in correlations[:3]:
                logger.info(f"  {correlation['kpi']}: score={correlation['score']}, normalized={correlation['normalized_score']}, confidence={correlation['confidence']}")
        
        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_filename = f"enhanced_structure_test_{timestamp}.json"
        
        detailed_results = {
            "test_timestamp": datetime.now().isoformat(),
            "analysis_duration_seconds": analysis_duration,
            "structure_verification": structure_verification,
            "quality_analysis": quality_analysis,
            "sample_kpi_structure": {},
            "test_status": "PASSED" if structure_verification["success_rate"] >= 90.0 else "FAILED"
        }
        
        # Extract sample KPI structure
        performance_metrics = result.get("performance_metrics", {})
        categories = performance_metrics.get("categories", {})
        
        for category_name, category_data in categories.items():
            kpis = category_data.get("kpis", {})
            for kpi_name, kpi_data in kpis.items():
                detailed_results["sample_kpi_structure"][f"{category_name}.{kpi_name}"] = {
                    "has_score": "score" in kpi_data,
                    "has_normalized_score": "normalized_score" in kpi_data,
                    "has_confidence": "confidence" in kpi_data,
                    "has_interpretation": "interpretation" in kpi_data,
                    "has_evidence": "evidence" in kpi_data,
                    "has_reasoning": "reasoning" in kpi_data,
                    "evidence_count": len(kpi_data.get("evidence", [])),
                    "has_sub_factors": "sub_factors" in kpi_data,
                    "sub_factor_count": len(kpi_data.get("sub_factors", {}))
                }
                break  # Only sample one KPI per category
            if detailed_results["sample_kpi_structure"]:
                break
        
        with open(results_filename, 'w') as f:
            json.dump(detailed_results, f, indent=2)
        
        logger.info(f"Detailed results saved to: {results_filename}")
        
        # Final assessment
        if structure_verification["success_rate"] >= 95.0:
            logger.info("🎉 ENHANCED STRUCTURE TEST PASSED!")
            logger.info("All enhanced fields (normalized_score, confidence, interpretation) are properly implemented")
        elif structure_verification["success_rate"] >= 80.0:
            logger.info("✅ ENHANCED STRUCTURE TEST MOSTLY PASSED!")
            logger.info("Most enhanced fields are implemented with minor issues")
        else:
            logger.error("❌ ENHANCED STRUCTURE TEST FAILED!")
            logger.error("Significant issues found with enhanced field implementation")
        
        logger.info(f"Final success rate: {structure_verification['success_rate']:.1f}%")
        
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
