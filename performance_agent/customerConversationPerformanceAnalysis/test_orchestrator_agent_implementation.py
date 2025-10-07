#!/usr/bin/env python3

"""
Test script for Orchestrator Agent implementation
Tests the per-category LLM analysis approach to avoid incomplete responses
"""

import os
import sys
import json
import logging
from datetime import datetime

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from models import ConversationData, Tweet, Classification
    from orchestrator_agent_service import OrchestratorAgent, create_orchestrator_agent
    from config_loader import config_loader
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'orchestrator_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)

logger = logging.getLogger(__name__)


def create_sample_conversation() -> ConversationData:
    """Create a sample conversation for testing"""
    
    tweets = [
        Tweet(
            tweet_id=1,
            text="Hi @XYZSupport, I'm having trouble accessing my account. I keep getting locked out when I try to log in.",
            created_at="2024-01-15T10:00:00Z",
            role="Customer",
            author_id="customer_123",
            inbound=True
        ),
        Tweet(
            tweet_id=2, 
            text="Hi there! I'm delighted to help you with your account access issue. I understand how frustrating it can be when you can't access your account. Let me assist you right away.",
            created_at="2024-01-15T10:05:00Z",
            role="Agent",
            author_id="agent_456",
            inbound=False
        ),
        Tweet(
            tweet_id=3,
            text="Thank you! I've been trying for the past hour and it's really frustrating. My username is john_doe123 but I can't remember if I need to use my email instead.",
            created_at="2024-01-15T10:07:00Z", 
            role="Customer",
            author_id="customer_123",
            inbound=True
        ),
        Tweet(
            tweet_id=4,
            text="I completely understand your frustration. For account verification and security, please DM me your email address and I'll help you unlock your account right away. I can also assist with a manual password reset if needed.",
            created_at="2024-01-15T10:10:00Z",
            role="Agent", 
            author_id="agent_456",
            inbound=False
        ),
        Tweet(
            tweet_id=5,  
            text="Perfect! I'll DM you now. Thank you so much for the quick help!",
            created_at="2024-01-15T10:12:00Z",
            role="Customer",
            author_id="customer_123",
            inbound=True
        ),
        Tweet(
            tweet_id=6,
            text="You're very welcome! I've successfully unlocked your account and sent you a password reset link via email. Your account should be working perfectly now. Is there anything else I can help you with today?",
            created_at="2024-01-15T10:20:00Z",
            role="Agent",
            author_id="agent_456",
            inbound=False
        ),
        Tweet(
            tweet_id=7,
            text="Amazing! Everything is working perfectly now. Thank you so much for the excellent help - you've made my day!",
            created_at="2024-01-15T10:25:00Z",
            role="Customer", 
            author_id="customer_123",
            inbound=True
        )
    ]
    
    classification = Classification(
        categorization="Technical Support",
        intent="Account Access Issue", 
        topic="Login Problems",
        sentiment="Positive"
    )
    
    return ConversationData(
        tweets=tweets,
        classification=classification
    )


def test_orchestrator_sequential_analysis():
    """Test orchestrator with sequential category analysis"""
    
    logger.info("=== Testing Orchestrator Agent (Sequential Analysis) ===")
    
    try:
        # Create orchestrator agent for sequential analysis
        orchestrator = create_orchestrator_agent(
            model_name="claude-4",
            temperature=0.1,
            max_retries=2,
            parallel_categories=False  # Sequential analysis
        )
        
        # Create sample conversation
        conversation_data = create_sample_conversation()
        logger.info(f"Created sample conversation with {len(conversation_data.tweets)} tweets")
        
        # Perform comprehensive analysis
        logger.info("Starting orchestrator-based sequential analysis...")
        start_time = datetime.now()
        
        results = orchestrator.analyze_conversation_comprehensive(conversation_data)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info(f"Sequential analysis completed in {duration:.2f} seconds")
        
        # Validate results
        if "error" in results:
            logger.error(f"Analysis failed with error: {results['error']}")
            return False
        
        # Check performance metrics structure
        performance_metrics = results.get("performance_metrics", {}) 
        categories = performance_metrics.get("categories", {})
        metadata = performance_metrics.get("metadata", {})
        
        logger.info(f"Analysis Summary:")
        logger.info(f"  - Total categories analyzed: {metadata.get('total_categories_analyzed', 0)}")
        logger.info(f"  - Total KPIs evaluated: {metadata.get('total_kpis_evaluated', 0)}")
        logger.info(f"  - Analysis duration: {metadata.get('analysis_duration_seconds', 0):.2f}s")
        
        # Check each category
        for category_name, category_data in categories.items():
            kpi_count = len(category_data.get('kpis', {}))
            category_score = category_data.get('category_score', 0)
            has_error = 'error' in category_data
            
            status = "✗ FAILED" if has_error else "✓ SUCCESS"
            logger.info(f"  - {category_name}: {status} ({kpi_count} KPIs, score: {category_score})")
            
            if has_error:
                logger.error(f"    Error: {category_data['error']}")
        
        # Check overall performance
        overall_performance = results.get("overall_performance", {})
        overall_score = overall_performance.get("overall_score", 0)
        performance_level = overall_performance.get("performance_level", "Unknown")
        
        logger.info(f"Overall Performance:")
        logger.info(f"  - Score: {overall_score}/10")
        logger.info(f"  - Level: {performance_level}")
        
        # Save results for inspection
        output_file = f"orchestrator_sequential_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Results saved to: {output_file}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error in sequential orchestrator test: {e}")
        return False


def test_orchestrator_parallel_analysis():
    """Test orchestrator with parallel category analysis"""
    
    logger.info("=== Testing Orchestrator Agent (Parallel Analysis) ===")
    
    try:
        # Create orchestrator agent for parallel analysis
        orchestrator = create_orchestrator_agent(
            model_name="claude-4",
            temperature=0.1, 
            max_retries=2,
            parallel_categories=True  # Parallel analysis
        )
        
        # Create sample conversation
        conversation_data = create_sample_conversation()
        logger.info(f"Created sample conversation with {len(conversation_data.tweets)} tweets")
        
        # Perform comprehensive analysis
        logger.info("Starting orchestrator-based parallel analysis...")
        start_time = datetime.now()
        
        results = orchestrator.analyze_conversation_comprehensive(conversation_data)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info(f"Parallel analysis completed in {duration:.2f} seconds")
        
        # Validate results
        if "error" in results:
            logger.error(f"Analysis failed with error: {results['error']}")
            return False
        
        # Check performance metrics structure
        performance_metrics = results.get("performance_metrics", {})
        categories = performance_metrics.get("categories", {})  
        metadata = performance_metrics.get("metadata", {})
        
        logger.info(f"Analysis Summary:")
        logger.info(f"  - Total categories analyzed: {metadata.get('total_categories_analyzed', 0)}")
        logger.info(f"  - Total KPIs evaluated: {metadata.get('total_kpis_evaluated', 0)}")
        logger.info(f"  - Analysis duration: {metadata.get('analysis_duration_seconds', 0):.2f}s")
        
        # Check each category
        for category_name, category_data in categories.items():
            kpi_count = len(category_data.get('kpis', {}))
            category_score = category_data.get('category_score', 0)
            has_error = 'error' in category_data
            
            status = "✗ FAILED" if has_error else "✓ SUCCESS"
            logger.info(f"  - {category_name}: {status} ({kpi_count} KPIs, score: {category_score})")
            
            if has_error:
                logger.error(f"    Error: {category_data['error']}")
        
        # Check overall performance
        overall_performance = results.get("overall_performance", {})
        overall_score = overall_performance.get("overall_score", 0)
        performance_level = overall_performance.get("performance_level", "Unknown")
        
        logger.info(f"Overall Performance:")
        logger.info(f"  - Score: {overall_score}/10")
        logger.info(f"  - Level: {performance_level}")
        
        # Save results for inspection
        output_file = f"orchestrator_parallel_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Results saved to: {output_file}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error in parallel orchestrator test: {e}")
        return False


def test_configuration_loading():
    """Test that configuration is loaded correctly for orchestrator"""
    
    logger.info("=== Testing Configuration Loading ===")
    
    try:
        # Test config loading
        config = config_loader.load_config()
        all_categories = list(config_loader.get_all_categories())
        
        logger.info(f"Configuration loaded successfully")
        logger.info(f"Available categories: {all_categories}")
        
        total_kpis = 0
        for category_name in all_categories:
            category_kpis = config_loader.get_category_kpis(category_name)
            kpi_count = len(category_kpis)
            total_kpis += kpi_count
            logger.info(f"  - {category_name}: {kpi_count} KPIs")
            
            # Show first few KPIs for each category
            kpi_names = list(category_kpis.keys())[:3]
            if kpi_names:
                logger.info(f"    Sample KPIs: {', '.join(kpi_names)}")
        
        logger.info(f"Total KPIs across all categories: {total_kpis}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing configuration: {e}")
        return False


def compare_sequential_vs_parallel():
    """Compare sequential vs parallel analysis performance"""
    
    logger.info("=== Comparing Sequential vs Parallel Analysis ===")
    
    try:
        conversation_data = create_sample_conversation()
        
        # Test sequential
        logger.info("Testing sequential analysis...")
        sequential_orchestrator = create_orchestrator_agent(parallel_categories=False)
        
        start_time = datetime.now()
        sequential_results = sequential_orchestrator.analyze_conversation_comprehensive(conversation_data)
        sequential_duration = (datetime.now() - start_time).total_seconds()
        
        # Test parallel  
        logger.info("Testing parallel analysis...")
        parallel_orchestrator = create_orchestrator_agent(parallel_categories=True)
        
        start_time = datetime.now()
        parallel_results = parallel_orchestrator.analyze_conversation_comprehensive(conversation_data)
        parallel_duration = (datetime.now() - start_time).total_seconds()
        
        # Compare results
        logger.info(f"Performance Comparison:")
        logger.info(f"  Sequential: {sequential_duration:.2f}s")
        logger.info(f"  Parallel: {parallel_duration:.2f}s")
        logger.info(f"  Speed improvement: {((sequential_duration - parallel_duration) / sequential_duration * 100):.1f}%")
        
        # Compare success rates
        seq_success = len([c for c in sequential_results.get("performance_metrics", {}).get("categories", {}).values() if not c.get('error')])
        par_success = len([c for c in parallel_results.get("performance_metrics", {}).get("categories", {}).values() if not c.get('error')])
        
        total_categories = len(sequential_results.get("performance_metrics", {}).get("categories", {}))
        
        logger.info(f"Success Rate Comparison:")
        logger.info(f"  Sequential: {seq_success}/{total_categories} ({seq_success/total_categories*100:.1f}%)")
        logger.info(f"  Parallel: {par_success}/{total_categories} ({par_success/total_categories*100:.1f}%)")
        
        return True
        
    except Exception as e:
        logger.error(f"Error in comparison test: {e}")
        return False


def main():
    """Run all orchestrator agent tests"""
    
    logger.info("Starting Orchestrator Agent Implementation Tests")
    logger.info("=" * 60)
    
    test_results = {}
    
    # Test configuration loading
    test_results["config_loading"] = test_configuration_loading()
    
    # Test sequential analysis
    test_results["sequential_analysis"] = test_orchestrator_sequential_analysis()
    
    # Test parallel analysis
    test_results["parallel_analysis"] = test_orchestrator_parallel_analysis()
    
    # Compare sequential vs parallel
    test_results["comparison"] = compare_sequential_vs_parallel()
    
    # Print summary
    logger.info("=" * 60)
    logger.info("TEST SUMMARY:")
    logger.info("=" * 60)
    
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result)
    
    for test_name, result in test_results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        logger.info(f"  {test_name}: {status}")
    
    logger.info(f"\nOverall: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests*100:.1f}%)")
    
    if passed_tests == total_tests:
        logger.info("🎉 All tests passed! Orchestrator Agent is working correctly.")
    else:
        logger.warning(f"⚠️  {total_tests - passed_tests} test(s) failed. Check the logs for details.")
    
    return passed_tests == total_tests


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
