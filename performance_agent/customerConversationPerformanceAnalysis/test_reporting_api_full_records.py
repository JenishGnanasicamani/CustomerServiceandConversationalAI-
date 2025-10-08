#!/usr/bin/env python3
"""
Test script for Reporting API - Fetch all records from agentic_analysis collection
This script calls the reporting API with maximum date range to get all records
and saves the selected records to a JSON file.
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

class ReportingAPITester:
    """Test class for calling the Reporting API and fetching all records"""
    
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
    
    def generate_full_report_post(self, customer: Optional[str] = 'Delta') -> Optional[Dict[str, Any]]:
        """
        Generate a report with maximum date range using POST method
        
        Args:
            customer: Optional customer filter. Use None or 'all' for all customers
            
        Returns:
            Report data or None if failed
        """
        try:
            # Use maximum date range to get all records
            # From year 2000 to year 2100 to ensure we capture all possible records
            start_date = "2000-01-01"
            end_date = "2100-12-31"
            
            request_data = {
                "start_date": start_date,
                "end_date": end_date
            }
            
            # Add customer filter if specified
            if customer and customer.lower() != 'all':
                request_data["customer"] = customer
            
            logger.info(f"Generating full report with POST method...")
            logger.info(f"Request data: {request_data}")
            
            response = self.session.post(
                f"{self.api_base_url}/reports/generate",
                json=request_data
            )
            
            if response.status_code == 200:
                report_data = response.json()
                logger.info(f"Report generated successfully!")
                logger.info(f"Status: {report_data.get('status')}")
                
                query_params = report_data.get('query_parameters', {})
                logger.info(f"Records found: {query_params.get('records_found', 0)}")
                
                selected_records = report_data.get('selected_records', [])
                logger.info(f"Selected records count: {len(selected_records)}")
                
                return report_data
            else:
                logger.error(f"Failed to generate report: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to generate report: {e}")
            return None
    
    def generate_full_report_get(self, customer: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Generate a report with maximum date range using GET method
        
        Args:
            customer: Optional customer filter. Use None or 'all' for all customers
            
        Returns:
            Report data or None if failed
        """
        try:
            # Use maximum date range to get all records
            start_date = "2000-01-01"
            end_date = "2100-12-31"
            
            params = {
                "start_date": start_date,
                "end_date": end_date
            }
            
            # Add customer filter if specified
            if customer and customer.lower() != 'all':
                params["customer"] = customer
            
            logger.info(f"Generating full report with GET method...")
            logger.info(f"Query parameters: {params}")
            
            response = self.session.get(
                f"{self.api_base_url}/reports/generate",
                params=params
            )
            
            if response.status_code == 200:
                report_data = response.json()
                logger.info(f"Report generated successfully!")
                logger.info(f"Status: {report_data.get('status')}")
                
                query_params = report_data.get('query_parameters', {})
                logger.info(f"Records found: {query_params.get('records_found', 0)}")
                
                selected_records = report_data.get('selected_records', [])
                logger.info(f"Selected records count: {len(selected_records)}")
                
                return report_data
            else:
                logger.error(f"Failed to generate report: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to generate report: {e}")
            return None
    
    def save_records_to_json(self, report_data: Dict[str, Any], filename: Optional[str] = None) -> str:
        """
        Save the selected records from report to a JSON file
        
        Args:
            report_data: Report data containing selected_records
            filename: Optional filename. If not provided, will generate timestamp-based name
            
        Returns:
            Filename of the saved file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reporting_api_records_{timestamp}.json"
        
        # Extract selected records
        selected_records = report_data.get('selected_records', [])
        
        # Prepare output data with metadata
        output_data = {
            "metadata": {
                "extraction_timestamp": datetime.now().isoformat(),
                "source_api": "reporting_api",
                "total_records": len(selected_records),
                "query_parameters": report_data.get('query_parameters', {}),
                "report_status": report_data.get('status'),
                "api_version": "1.0.0"
            },
            "selected_records": selected_records,
            "summary": report_data.get('summary', {}),
            "aggregated_insights": report_data.get('aggregated_insights', {}),
            "report_metadata": report_data.get('report_metadata', {})
        }
        
        # Save to JSON file
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"Records saved to: {filename}")
        logger.info(f"Total records saved: {len(selected_records)}")
        
        return filename
    
    def run_comprehensive_test(self, customer: Optional[str] = None, method: str = "POST") -> Optional[str]:
        """
        Run comprehensive test of the reporting API
        
        Args:
            customer: Optional customer filter
            method: HTTP method to use ("POST" or "GET")
            
        Returns:
            Filename of saved records or None if failed
        """
        logger.info("="*60)
        logger.info("COMPREHENSIVE REPORTING API TEST")
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
        
        # Step 3: Generate report
        logger.info(f"\n3. Generating Full Report using {method} method...")
        if method.upper() == "POST":
            report_data = self.generate_full_report_post(customer)
        else:
            report_data = self.generate_full_report_get(customer)
        
        if not report_data:
            logger.error("Failed to generate report. Aborting test.")
            return None
        
        # Step 4: Save records to JSON
        logger.info("\n4. Saving Records to JSON File...")
        filename = self.save_records_to_json(report_data)
        
        # Step 5: Summary
        logger.info("\n5. Test Summary:")
        logger.info(f"   - Method Used: {method}")
        logger.info(f"   - Customer Filter: {customer or 'All customers'}")
        logger.info(f"   - Records Retrieved: {len(report_data.get('selected_records', []))}")
        logger.info(f"   - Output File: {filename}")
        logger.info(f"   - Report Status: {report_data.get('status')}")
        
        logger.info("\n" + "="*60)
        logger.info("TEST COMPLETED SUCCESSFULLY")
        logger.info("="*60)
        
        return filename


def main():
    """Main function to run the test"""
    # Configuration
    API_BASE_URL = os.getenv('REPORTING_API_URL', 'http://localhost:8003')
    CUSTOMER_FILTER = os.getenv('CUSTOMER_FILTER', None)  # Set to None for all customers
    HTTP_METHOD = os.getenv('HTTP_METHOD', 'POST')  # POST or GET
    
    logger.info("Starting Reporting API Test...")
    logger.info(f"API Base URL: {API_BASE_URL}")
    logger.info(f"Customer Filter: {CUSTOMER_FILTER or 'All customers'}")
    logger.info(f"HTTP Method: {HTTP_METHOD}")
    
    # Create tester instance
    tester = ReportingAPITester(API_BASE_URL)
    
    # Run comprehensive test
    try:
        output_file = tester.run_comprehensive_test(
            customer=CUSTOMER_FILTER,
            method=HTTP_METHOD
        )
        
        if output_file:
            logger.info(f"\nTest completed successfully!")
            logger.info(f"Records saved to: {output_file}")
            
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
