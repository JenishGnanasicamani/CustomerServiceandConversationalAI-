#!/usr/bin/env python3
"""
Test script to identify and fix text truncation issues in reasoning fields
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_text_truncation_issue():
    """Test and identify text truncation issues in reasoning fields"""
    
    print("=" * 80)
    print("TEXT TRUNCATION INVESTIGATION")
    print("=" * 80)
    
    try:
        # Connect to MongoDB to examine the actual stored data
        from pymongo import MongoClient
        
        # Use environment variable for connection string
        connection_string = os.getenv('MONGODB_CONNECTION_STRING', 'mongodb://localhost:27017/')
        client = MongoClient(connection_string)
        db = client['csai']
        collection = db['agentic_analysis']
        
        print(f"✓ Connected to MongoDB")
        
        # Find the record with truncated text
        record = collection.find_one({"_id": "68e29bf2930aa38de5fced12"})
        
        if not record:
            print("❌ Record not found")
            return False
        
        print(f"✓ Found record with conversation_id: {record.get('conversation_id')}")
        
        # Extract the reasoning text that's being truncated
        categories = record.get('performance_metrics', {}).get('categories', {})
        
        truncation_found = False
        
        for category_name, category_data in categories.items():
            kpis = category_data.get('kpis', {})
            
            for kpi_name, kpi_data in kpis.items():
                reason = kpi_data.get('reason', '')
                
                # Check for truncation indicators
                if reason.endswith('…') or len(reason) > 100:
                    print(f"\n🔍 TRUNCATION FOUND:")
                    print(f"   Category: {category_name}")
                    print(f"   KPI: {kpi_name}")
                    print(f"   Reason length: {len(reason)} characters")
                    print(f"   Truncated text: {reason[:100]}...")
                    print(f"   Ends with ellipsis: {reason.endswith('…')}")
                    truncation_found = True
                
                # Check sub-KPIs
                sub_kpis = kpi_data.get('sub_kpis', {})
                for sub_kpi_name, sub_kpi_data in sub_kpis.items():
                    sub_reason = sub_kpi_data.get('reason', '')
                    
                    if sub_reason.endswith('…') or len(sub_reason) > 150:
                        print(f"\n🔍 SUB-KPI TRUNCATION FOUND:")
                        print(f"   Category: {category_name}")
                        print(f"   KPI: {kpi_name}")
                        print(f"   Sub-KPI: {sub_kpi_name}")
                        print(f"   Reason length: {len(sub_reason)} characters")
                        print(f"   Truncated text: {sub_reason[:100]}...")
                        print(f"   Ends with ellipsis: {sub_reason.endswith('…')}")
                        truncation_found = True
        
        if not truncation_found:
            print("✓ No text truncation found")
        
        # Save full record for analysis
        with open('full_record_analysis.json', 'w') as f:
            json.dump(record, f, indent=2, default=str)
        
        print(f"\n✓ Full record saved to: full_record_analysis.json")
        
        client.close()
        return not truncation_found
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


def investigate_mongodb_field_limits():
    """Investigate if MongoDB has field size limitations causing truncation"""
    
    print("\n" + "=" * 80)
    print("MONGODB FIELD SIZE INVESTIGATION")
    print("=" * 80)
    
    try:
        from pymongo import MongoClient
        
        connection_string = os.getenv('MONGODB_CONNECTION_STRING', 'mongodb://localhost:27017/')
        client = MongoClient(connection_string)
        db = client['csai']
        
        # Test inserting a document with very long text
        test_collection = db['text_size_test']
        
        # Create a very long reasoning text
        long_text = "This is a very detailed analysis of the customer service interaction. " * 100
        print(f"✓ Testing with text length: {len(long_text)} characters")
        
        test_doc = {
            "_id": "test_long_text",
            "short_field": "short text",
            "long_reasoning": long_text,
            "test_timestamp": datetime.now()
        }
        
        # Insert test document
        result = test_collection.replace_one({"_id": "test_long_text"}, test_doc, upsert=True)
        print(f"✓ Inserted test document")
        
        # Retrieve and check
        retrieved_doc = test_collection.find_one({"_id": "test_long_text"})
        retrieved_text = retrieved_doc.get('long_reasoning', '')
        
        print(f"✓ Retrieved text length: {len(retrieved_text)} characters")
        print(f"✓ Text preserved fully: {len(retrieved_text) == len(long_text)}")
        
        if len(retrieved_text) != len(long_text):
            print(f"❌ TEXT TRUNCATION DETECTED IN MONGODB!")
            print(f"   Original length: {len(long_text)}")
            print(f"   Retrieved length: {len(retrieved_text)}")
        else:
            print(f"✅ MongoDB can handle long text fields - issue is elsewhere")
        
        # Clean up test
        test_collection.delete_one({"_id": "test_long_text"})
        
        client.close()
        return len(retrieved_text) == len(long_text)
        
    except Exception as e:
        print(f"❌ MongoDB field size test failed: {e}")
        return False


def check_llm_service_text_generation():
    """Check if the LLM service is generating full reasoning text"""
    
    print("\n" + "=" * 80)  
    print("LLM SERVICE TEXT GENERATION CHECK")
    print("=" * 80)
    
    try:
        from src.llm_agent_service import get_llm_agent_service
        from src.models import ConversationData, Tweet, Classification
        
        # Create test conversation
        test_tweets = [
            Tweet(
                tweet_id=1,
                author_id="Delta",
                role="Customer",
                inbound=True,
                created_at="2025-10-05T21:54:39",
                text="I need help with my flight booking issue"
            ),
            Tweet(
                tweet_id=2,
                author_id="support_agent",
                role="Agent", 
                inbound=False,
                created_at="2025-10-05T21:55:00",
                text="I'll be happy to help you with your flight booking. Let me look into that for you right away."
            )
        ]
        
        test_classification = Classification(
            categorization="Travel/Flight",
            intent="Booking Issue",
            topic="Flight",
            sentiment="Neutral"
        )
        
        conversation_data = ConversationData(
            tweets=test_tweets,
            classification=test_classification
        )
        
        print(f"✓ Created test conversation with {len(test_tweets)} messages")
        
        # Get LLM service
        llm_service = get_llm_agent_service()
        print(f"✓ LLM service initialized: {llm_service.model_name}")
        
        # Analyze conversation
        print(f"🔄 Analyzing conversation...")
        analysis_result = llm_service.analyze_conversation_performance(conversation_data)
        
        print(f"✓ Analysis completed")
        
        # Check reasoning text lengths in the raw result
        categories = analysis_result.get("performance_metrics", {}).get("categories", {})
        
        text_length_issues = []
        full_reasoning_texts = []
        
        for category_name, category_data in categories.items():
            kpis = category_data.get('kpis', {})
            
            for kpi_name, kpi_data in kpis.items():
                reason = kpi_data.get('reasoning', '') or kpi_data.get('reason', '')
                
                if reason:
                    full_reasoning_texts.append({
                        'category': category_name,
                        'kpi': kpi_name,
                        'length': len(reason),
                        'text': reason[:200] + '...' if len(reason) > 200 else reason,
                        'full_text': reason
                    })
                    
                    if len(reason) < 50:
                        text_length_issues.append(f"{category_name}.{kpi_name}: only {len(reason)} chars")
        
        print(f"\n📊 LLM SERVICE REASONING TEXT ANALYSIS:")
        print(f"   Total reasoning texts generated: {len(full_reasoning_texts)}")
        
        for item in full_reasoning_texts:
            print(f"   - {item['category']}.{item['kpi']}: {item['length']} characters")
            print(f"     Preview: {item['text']}")
        
        if text_length_issues:
            print(f"\n⚠️  SHORT REASONING TEXTS FOUND:")
            for issue in text_length_issues:
                print(f"   - {issue}")
        else:
            print(f"\n✅ All reasoning texts are appropriately detailed")
        
        # Save full LLM output for analysis
        with open('llm_full_output_analysis.json', 'w') as f:
            json.dump(analysis_result, f, indent=2, default=str)
        
        with open('llm_reasoning_texts.json', 'w') as f:
            json.dump(full_reasoning_texts, f, indent=2, default=str)
        
        print(f"\n✓ Full LLM output saved to: llm_full_output_analysis.json")
        print(f"✓ Reasoning texts saved to: llm_reasoning_texts.json")
        
        return len(text_length_issues) == 0
        
    except Exception as e:
        print(f"❌ LLM service text check failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_periodic_job_text_processing():
    """Check if periodic job service is truncating text during processing"""
    
    print("\n" + "=" * 80)
    print("PERIODIC JOB TEXT PROCESSING CHECK")
    print("=" * 80)
    
    try:
        from src.periodic_job_service import PeriodicJobService
        
        # Create mock service
        service = PeriodicJobService("mongodb://test", "test_db")
        
        # Create mock raw result with long reasoning text
        long_reasoning = "This is a comprehensive analysis of customer service performance that includes detailed evaluation of agent response quality, empathy demonstration, problem-solving approach, communication effectiveness, and overall customer satisfaction metrics. The agent showed excellent understanding of the customer's needs and provided thorough assistance throughout the interaction."
        
        mock_raw_result = {
            "conversation_id": "test_conv_123",
            "analysis_timestamp": datetime.now().isoformat(),
            "analysis_method": "LLM-based Agent Analysis",
            "performance_metrics": {
                "categories": {
                    "empathy_communication": {
                        "category_score": 8.0,
                        "kpis": {
                            "empathy_score": {
                                "score": 8.0,
                                "reasoning": long_reasoning,  # Long text that should not be truncated
                                "evidence": ["Good empathetic response"]
                            }
                        }
                    }
                }
            }
        }
        
        print(f"✓ Created mock result with reasoning length: {len(long_reasoning)} characters")
        
        # Mock conversation data
        from src.models import ConversationData, Tweet, Classification
        
        conversation_data = ConversationData(
            tweets=[Tweet(tweet_id=1, author_id="test", role="Customer", inbound=True, created_at="2025-01-01", text="test")],
            classification=Classification(categorization="Test", intent="Test", topic="Test", sentiment="Neutral")
        )
        
        customer_info = {"customer": "TestCustomer", "created_at": "2025-01-01", "created_time": "12:00:00"}
        source_record = {"_id": "test123", "conversation_number": "CONV-TEST-123"}
        
        # Process through restructuring
        restructured = service._restructure_analysis_result(
            mock_raw_result,
            conversation_data, 
            customer_info,
            source_record
        )
        
        # Check if reasoning text was preserved
        empathy_kpi = restructured.get('performance_metrics', {}).get('categories', {}).get('empathy_communication', {}).get('kpis', {}).get('empathy_score', {})
        processed_reasoning = empathy_kpi.get('reason', '')
        
        print(f"✓ Processed reasoning length: {len(processed_reasoning)} characters")
        
        if len(processed_reasoning) == len(long_reasoning):
            print(f"✅ Text preserved fully in periodic job processing")
            text_preserved = True
        elif processed_reasoning == long_reasoning:
            print(f"✅ Text content matches exactly")
            text_preserved = True
        else:
            print(f"❌ TEXT TRUNCATION IN PERIODIC JOB PROCESSING!")
            print(f"   Original: {len(long_reasoning)} chars")
            print(f"   Processed: {len(processed_reasoning)} chars")
            print(f"   Original preview: {long_reasoning[:100]}...")
            print(f"   Processed preview: {processed_reasoning[:100]}...")
            text_preserved = False
        
        # Save comparison for analysis
        comparison = {
            "original_reasoning": long_reasoning,
            "processed_reasoning": processed_reasoning,
            "original_length": len(long_reasoning),
            "processed_length": len(processed_reasoning),
            "text_preserved": text_preserved,
            "full_restructured_result": restructured
        }
        
        with open('periodic_job_text_analysis.json', 'w') as f:
            json.dump(comparison, f, indent=2, default=str)
        
        print(f"✓ Comparison saved to: periodic_job_text_analysis.json")
        
        return text_preserved
        
    except Exception as e:
        print(f"❌ Periodic job text check failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all text truncation investigation tests"""
    
    print("🔍 TEXT TRUNCATION INVESTIGATION")
    print("Investigating why reasoning text is being truncated in MongoDB records")
    print(f"Test run at: {datetime.now().isoformat()}")
    
    all_tests_passed = True
    
    # Test 1: Check actual MongoDB record
    test1_passed = test_text_truncation_issue()
    all_tests_passed = all_tests_passed and test1_passed
    
    # Test 2: Check MongoDB field size limits
    test2_passed = investigate_mongodb_field_limits()
    all_tests_passed = all_tests_passed and test2_passed
    
    # Test 3: Check LLM service text generation
    test3_passed = check_llm_service_text_generation()
    all_tests_passed = all_tests_passed and test3_passed
    
    # Test 4: Check periodic job text processing
    test4_passed = check_periodic_job_text_processing()
    all_tests_passed = all_tests_passed and test4_passed
    
    # Final summary
    print("\n" + "=" * 80)
    print("TEXT TRUNCATION INVESTIGATION SUMMARY")
    print("=" * 80)
    
    if all_tests_passed:
        print("✅ ALL TESTS PASSED - No truncation issues found")
    else:
        print("❌ TRUNCATION ISSUES DETECTED")
        print("\n🔧 Recommended Actions:")
        if not test1_passed:
            print("   - Text truncation found in MongoDB records")
        if not test2_passed:
            print("   - MongoDB field size limits detected")  
        if not test3_passed:
            print("   - LLM service generating short reasoning texts")
        if not test4_passed:
            print("   - Periodic job service truncating text during processing")
    
    return all_tests_passed


if __name__ == "__main__":
    main()
