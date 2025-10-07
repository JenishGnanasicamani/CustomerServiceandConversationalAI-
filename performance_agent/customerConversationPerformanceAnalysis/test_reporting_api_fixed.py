#!/usr/bin/env python3
"""
Fixed Reporting API Test Script - Uses current date to find actual records
"""

import json
import os
import requests
from datetime import datetime
import logging

def test_reporting_api_with_actual_data():
    """Test reporting API with current date to get actual records"""
    
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    api_url = "http://localhost:8003"
    today = datetime.now().strftime('%Y-%m-%d')
    
    logger.info("🧪 FIXED REPORTING API TEST - CURRENT DATE")
    logger.info("=" * 60)
    
    try:
        # Test with today's date specifically
        logger.info(f"Testing with today's date: {today}")
        
        response = requests.post(
            f"{api_url}/reports/generate",
            json={
                "start_date": today,
                "end_date": today
            },
            timeout=30
        )
        
        if response.status_code == 200:
            report = response.json()
            records = report.get('selected_records', [])
            
            logger.info(f"✅ SUCCESS: Found {len(records)} records")
            
            if len(records) > 0:
                logger.info("📊 SAMPLE RECORD DETAILS:")
                for i, record in enumerate(records[:2]):
                    logger.info(f"   Record {i+1}:")
                    logger.info(f"     ID: {record.get('_id')}")
                    logger.info(f"     Conversation ID: {record.get('conversation_id')}")
                    logger.info(f"     Customer: {record.get('customer')}")
                    logger.info(f"     Created: {record.get('created_at')}")
                
                # Save results
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"fixed_reporting_api_results_{timestamp}.json"
                
                with open(filename, 'w') as f:
                    json.dump(report, f, indent=2, default=str)
                
                logger.info(f"📁 Results saved to: {filename}")
                return True
            else:
                logger.info("⚠️  No records found even with today's date")
                return False
        else:
            logger.error(f"❌ API request failed: {response.status_code}")
            return False
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_reporting_api_with_actual_data()
    if success:
        print("\n✅ Fixed test completed successfully!")
    else:
        print("\n❌ Test still has issues - check MongoDB data dates")
