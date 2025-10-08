#!/usr/bin/env python3
"""
Test script for Reporting API - Modified to work with actual MongoDB data structure
This script handles the actual data format found in the agentic_analysis collection
"""

import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ReportingAPITesterActualData:
    """Test class for calling the Reporting API with actual data structure understanding"""
    
    def __init__(self, api_base_url: str = "http://localhost:8003"):
        """
        Initialize the tester
        
        Args:
            api_base_url: Base URL for the reporting API
        """
        self.api_base_url = api_base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def test_api_health(self) -> bool:
        """Test if the API is healthy and accessible"""
        try:
            response = self.session.get(f"{self.api_base_url}/health")
            if response.status_code == 200:
                health_data = response.json()
                logger.info(f"API Health Status: {health_data.get('status', 'unknown')}")
                logger.info(f"Database Connected: {health_data.get('database_connected', False)}")
                logger.info(f"LLM Service Available: {health_data.get('llm_service_available', False)}")
                return health_data.get('status') == 'healthy'
            else:
                logger.error(f"Health check failed with status code: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to connect to API for health check: {e}")
            return False
    
    def get_collection_stats(self) -> Optional[Dict[str, Any]]:
        """Get collection statistics to understand the data range"""
        try:
            response = self.session.get(f"{self.api_base_url}/reports/stats")
            if response.status_code == 200:
                stats = response.json()
                logger.info(f"Collection Stats:")
                logger.info(f"  Total Records: {stats.get('total_records', 0)}")
                logger.info(f"  Unique Customers: {stats.get('unique_customers', 0)}")
                logger.info(f"  Recent Records (30 days): {stats.get('recent_records_30_days', 0)}")
                
                date_range = stats.get('date_range', {})
                if date_range.get('earliest_record'):
                    logger.info(f"  Earliest Record: {date_range['earliest_record']}")
                if date_range.get('latest_record'):
                    logger.info(f"  Latest Record: {date_range['latest_record']}")
                
                sample_customers = stats.get('sample_customers', [])
                if sample_customers:
                    logger.info(f"  Sample Customers: {sample_customers[:5]}")
                
                return stats
            else:
                logger.error(f"Failed to get collection stats: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get collection stats: {e}")
            return None
    
    def test_different_date_ranges_and_customers(self) -> Dict[str, Any]:
        """
        Test various date ranges and customer combinations to find what works
        
        Returns:
            Dictionary with test results
        """
        logger.info("🧪 Testing Different Date Ranges and Customer Filters...")
        
        test_results = {}
        
        # Test scenarios based on the actual data we found
        test_scenarios = [
            {
                "name": "Max Range - No Customer",
                "start_date": "2000-01-01",
                "end_date": "2100-12-31",
                "customer": None
            },
            {
                "name": "Max Range - All Customers",
                "start_date": "2000-01-01", 
                "end_date": "2100-12-31",
                "customer": "all"
            },
            {
                "name": "2025 Range - No Customer",
                "start_date": "2025-01-01",
                "end_date": "2025-12-31", 
                "customer": None
            },
            {
                "name": "Oct 2025 Range - No Customer",
                "start_date": "2025-10-01",
                "end_date": "2025-10-31",
                "customer": None
            },
            {
                "name": "Oct 4 2025 - No Customer",
                "start_date": "2025-10-04",
                "end_date": "2025-10-04",
                "customer": None
            },
            {
                "name": "Oct 4 2025 with Time - No Customer", 
                "start_date": "2025-10-04T00:00:00",
                "end_date": "2025-10-04T23:59:59",
                "customer": None
            },
            {
                "name": "Max Range - Customer Apple",
                "start_date": "2000-01-01",
                "end_date": "2100-12-31",
                "customer": "Apple"
            },
            {
                "name": "Max Range - Customer None",
                "start_date": "2000-01-01",  
                "end_date": "2100-12-31",
                "customer": "None"
            }
        ]
        
        for scenario in test_scenarios:
            logger.info(f"\n--- Testing: {scenario['name']} ---")
            
            try:
                request_data = {
                    "start_date": scenario["start_date"],
                    "end_date": scenario["end_date"]
                }
                
                if scenario["customer"]:
                    request_data["customer"] = scenario["customer"]
                
                response = self.session.post(
                    f"{self.api_base_url}/reports/generate",
                    json=request_data
                )
                
                if response.status_code == 200:
                    report_data = response.json()
                    records_count = len(report_data.get('selected_records', []))
                    
                    test_results[scenario['name']] = {
                        "success": True,
                        "records_found": records_count,
                        "status": report_data.get('status'),
                        "query_params": request_data
                    }
                    
                    logger.info(f"  ✅ Success: {records_count} records found")
                    
                    # If we found records, save them
                    if records_count > 0:
                        filename = f"successful_query_{scenario['name'].replace(' ', '_').replace('-', '_').lower()}.json"
                        with open(filename, 'w') as f:
                            json.dump(report_data, f, indent=2, default=str)
                        logger.info(f"  📁 Records saved to: {filename}")
                
                else:
                    test_results[scenario['name']] = {
                        "success": False,
                        "error": f"HTTP {response.status_code}",
                        "response": response.text[:200],
                        "query_params": request_data
                    }
                    logger.error(f"  ❌ Failed: HTTP {response.status_code}")
                    
            except Exception as e:
                test_results[scenario['name']] = {
                    "success": False,
                    "error": str(e),
                    "query_params": request_data
                }
                logger.error(f"  ❌ Exception: {e}")
        
        return test_results
    
    def analyze_results(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the test results to understand what works"""
        
        successful_tests = []
        failed_tests = []
        tests_with_records = []
        
        for test_name, result in test_results.items():
            if result.get('success'):
                successful_tests.append(test_name)
                if result.get('records_found', 0) > 0:
                    tests_with_records.append({
                        'name': test_name,
                        'count': result['records_found'],
                        'params': result['query_params']
                    })
            else:
                failed_tests.append(test_name)
        
        analysis = {
            "summary": {
                "total_tests": len(test_results),
                "successful_tests": len(successful_tests),
                "failed_tests": len(failed_tests),
                "tests_with_records": len(tests_with_records)
            },
            "successful_tests": successful_tests,
            "failed_tests": failed_tests,
            "tests_with_records": tests_with_records,
            "recommendations": []
        }
        
        # Generate recommendations
        if not tests_with_records:
            analysis["recommendations"].append("No queries returned records. The data structure may not match API expectations.")
            analysis["recommendations"].append("Consider checking if data uses 'timestamp' field instead of 'created_at'.")
            analysis["recommendations"].append("Verify customer field exists and has expected values.")
        else:
            analysis["recommendations"].append(f"Found {len(tests_with_records)} working query patterns.")
            for test in tests_with_records:
                analysis["recommendations"].append(f"Pattern '{test['name']}' returned {test['count']} records.")
        
        return analysis
    
    def run_comprehensive_test(self) -> Optional[str]:
        """
        Run comprehensive test to find working query patterns
        
        Returns:
            Filename of analysis results or None if failed
        """
        logger.info("="*60)
        logger.info("COMPREHENSIVE REPORTING API TEST - ACTUAL DATA STRUCTURE")
        logger.info("="*60)
        
        # Step 1: Test API health
        logger.info("\n1. Testing API Health...")
        if not self.test_api_health():
            logger.error("API is not healthy. Aborting test.")
            return None
        
        # Step 2: Get collection statistics
        logger.info("\n2. Getting Collection Statistics...")
        stats = self.get_collection_stats()
        if not stats:
            logger.warning("Could not get collection stats, but continuing...")
        
        # Step 3: Test different scenarios
        logger.info("\n3. Testing Different Query Scenarios...")
        test_results = self.test_different_date_ranges_and_customers()
        
        # Step 4: Analyze results
        logger.info("\n4. Analyzing Test Results...")
        analysis = self.analyze_results(test_results)
        
        # Step 5: Save comprehensive results
        logger.info("\n5. Saving Comprehensive Results...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reporting_api_comprehensive_test_{timestamp}.json"
        
        comprehensive_results = {
            "metadata": {
                "test_timestamp": datetime.now().isoformat(),
                "api_base_url": self.api_base_url,
                "test_type": "comprehensive_query_pattern_analysis"
            },
            "collection_stats": stats,
            "test_results": test_results,
            "analysis": analysis
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(comprehensive_results, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"Comprehensive results saved to: {filename}")
        
        # Step 6: Summary
        logger.info("\n6. Test Summary:")
        logger.info(f"   - Total Tests: {analysis['summary']['total_tests']}")
        logger.info(f"   - Successful: {analysis['summary']['successful_tests']}")
        logger.info(f"   - With Records: {analysis['summary']['tests_with_records']}")
        logger.info(f"   - Results File: {filename}")
        
        if analysis['tests_with_records']:
            logger.info(f"\n   🎉 Found working patterns:")
            for test in analysis['tests_with_records']:
                logger.info(f"     - {test['name']}: {test['count']} records")
        else:
            logger.warning(f"\n   ⚠️  No queries returned records - data structure mismatch likely")
        
        logger.info("\n   💡 Recommendations:")
        for rec in analysis['recommendations']:
            logger.info(f"     - {rec}")
        
        logger.info("\n" + "="*60)
        logger.info("COMPREHENSIVE TEST COMPLETED")
        logger.info("="*60)
        
        return filename


def main():
    """Main function to run the test"""
    # Configuration
    API_BASE_URL = os.getenv('REPORTING_API_URL', 'http://localhost:8003')
    
    logger.info("Starting Comprehensive Reporting API Test...")
    logger.info(f"API Base URL: {API_BASE_URL}")
    
    # Create tester instance
    tester = ReportingAPITesterActualData(API_BASE_URL)
    
    # Run comprehensive test
    try:
        output_file = tester.run_comprehensive_test()
        
        if output_file:
            logger.info(f"\nTest completed successfully!")
            logger.info(f"Results saved to: {output_file}")
            
            # Print file info
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                logger.info(f"File size: {file_size:,} bytes")
        else:
            logger.error("Test failed!")
            return 1
            
    except KeyboardInterrupt:
        logger.info("\nTest interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Test failed with exception: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
