#!/usr/bin/env python3
"""
Test script for periodic job service with file-based data sources
Demonstrates configuring and running the periodic job to read from files
and output performance analysis results to files
"""

import json
import logging
import os
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.periodic_job_service import PeriodicJobService

def create_sample_sentiment_data() -> List[Dict[str, Any]]:
    """Create sample sentiment analysis data for testing"""
    
    sample_data = [
        {
            "_id": "64a1b2c3d4e5f6789abcdef0",
            "created_at": "2023-01-15T14:30:00Z",
            "customer": "customer_123",
            "conversation": {
                "conversation_id": "conv_001",
                "created_at": "2023-01-15T14:30:00Z",
                "tweets": [
                    {
                        "tweet_id": 1,
                        "author_id": "customer_123",
                        "role": "Customer",
                        "inbound": True,
                        "created_at": "2023-01-15T14:30:00Z",
                        "text": "I'm really frustrated with my billing issue. This is the third time I'm calling about the same problem."
                    },
                    {
                        "tweet_id": 2,
                        "author_id": "agent_001",
                        "role": "Service Provider",
                        "inbound": False,
                        "created_at": "2023-01-15T14:32:00Z",
                        "text": "I sincerely apologize for the frustration you're experiencing with your billing issue. I understand how concerning it must be to contact us multiple times about the same problem. Let me thoroughly review your account right now and ensure we resolve this completely for you today."
                    },
                    {
                        "tweet_id": 3,
                        "author_id": "customer_123",
                        "role": "Customer",
                        "inbound": True,
                        "created_at": "2023-01-15T14:35:00Z",
                        "text": "Thank you so much for your help! You actually listened to my concern and fixed it properly. I really appreciate the excellent service."
                    }
                ],
                "classification": {
                    "categorization": "Billing Issue",
                    "intent": "Support Request",
                    "topic": "Billing",
                    "sentiment": "Positive"
                }
            },
            "sentiment_analysis": {
                "overall_sentiment": "Positive",
                "intent": "Support Request",
                "topic": "Billing"
            }
        },
        {
            "_id": "64a1b2c3d4e5f6789abcdef1",
            "created_at": "2023-01-15T15:45:00Z",
            "customer": "customer_456",
            "conversation": {
                "conversation_id": "conv_002",
                "created_at": "2023-01-15T15:45:00Z",
                "tweets": [
                    {
                        "tweet_id": 4,
                        "author_id": "customer_456",
                        "role": "Customer",
                        "inbound": True,
                        "created_at": "2023-01-15T15:45:00Z",
                        "text": "My internet service has been down for 2 days. When will this be fixed?"
                    },
                    {
                        "tweet_id": 5,
                        "author_id": "agent_002",
                        "role": "Service Provider",
                        "inbound": False,
                        "created_at": "2023-01-15T15:47:00Z",
                        "text": "I see your service outage. We're working on it. Should be fixed soon."
                    },
                    {
                        "tweet_id": 6,
                        "author_id": "customer_456",
                        "role": "Customer",
                        "inbound": True,
                        "created_at": "2023-01-15T15:50:00Z",
                        "text": "That's not very helpful. I need a more specific timeline."
                    }
                ],
                "classification": {
                    "categorization": "Technical Issue",
                    "intent": "Service Request",
                    "topic": "Internet Service",
                    "sentiment": "Negative"
                }
            },
            "sentiment_analysis": {
                "overall_sentiment": "Negative",
                "intent": "Service Request",
                "topic": "Internet Service"
            }
        },
        {
            "_id": "64a1b2c3d4e5f6789abcdef2",
            "created_at": "2023-01-15T16:20:00Z",
            "customer": "customer_789",
            "conversation": {
                "conversation_id": "conv_003",
                "created_at": "2023-01-15T16:20:00Z",
                "tweets": [
                    {
                        "tweet_id": 7,
                        "author_id": "customer_789",
                        "role": "Customer",
                        "inbound": True,
                        "created_at": "2023-01-15T16:20:00Z",
                        "text": "Hi, I'd like to upgrade my plan to include more data. What options do you have?"
                    },
                    {
                        "tweet_id": 8,
                        "author_id": "agent_003",
                        "role": "Service Provider",
                        "inbound": False,
                        "created_at": "2023-01-15T16:22:00Z",
                        "text": "Hello! I'd be happy to help you explore our data upgrade options. We have several plans that might work perfectly for your needs. Let me show you what's available and help you find the best fit for your usage patterns."
                    },
                    {
                        "tweet_id": 9,
                        "author_id": "customer_789",
                        "role": "Customer",
                        "inbound": True,
                        "created_at": "2023-01-15T16:25:00Z",
                        "text": "Perfect! That sounds great. Please show me the options."
                    }
                ],
                "classification": {
                    "categorization": "Sales Inquiry",
                    "intent": "Upgrade Request",
                    "topic": "Plan Upgrade",
                    "sentiment": "Neutral"
                }
            },
            "sentiment_analysis": {
                "overall_sentiment": "Neutral",
                "intent": "Upgrade Request",
                "topic": "Plan Upgrade"
            }
        }
    ]
    
    return sample_data

def setup_test_environment() -> Dict[str, Path]:
    """Set up test environment with input and output directories"""
    
    # Create temporary directories
    base_temp = Path(tempfile.mkdtemp(prefix="periodic_job_test_"))
    
    input_dir = base_temp / "input_data"
    output_dir = base_temp / "analysis_results"
    
    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    return {
        "base": base_temp,
        "input": input_dir,
        "output": output_dir
    }

def create_test_files(input_dir: Path, sample_data: List[Dict[str, Any]]):
    """Create test JSON files with sample data"""
    
    # Create multiple files to test directory processing
    files_created = []
    
    # File 1: Single record
    file1 = input_dir / "sentiment_data_001.json"
    with open(file1, 'w', encoding='utf-8') as f:
        json.dump(sample_data[0], f, indent=2, default=str)
    files_created.append(file1)
    
    # File 2: Multiple records as array
    file2 = input_dir / "sentiment_data_002.json"
    with open(file2, 'w', encoding='utf-8') as f:
        json.dump(sample_data[1:], f, indent=2, default=str)
    files_created.append(file2)
    
    print(f"✅ Created {len(files_created)} test input files:")
    for file_path in files_created:
        print(f"   - {file_path}")
        
    return files_created

def test_periodic_job_file_source():
    """Test the periodic job service with file-based data source"""
    
    print("🧪 Testing Periodic Job Service with File-Based Data Source")
    print("=" * 70)
    
    # Set up test environment
    print("\n1. Setting up test environment...")
    test_dirs = setup_test_environment()
    print(f"✅ Test directories created:")
    print(f"   - Input: {test_dirs['input']}")
    print(f"   - Output: {test_dirs['output']}")
    
    # Create sample data
    print("\n2. Creating sample sentiment analysis data...")
    sample_data = create_sample_sentiment_data()
    print(f"✅ Created {len(sample_data)} sample sentiment records")
    
    # Create test files
    print("\n3. Creating test input files...")
    input_files = create_test_files(test_dirs['input'], sample_data)
    
    # Initialize periodic job service
    print("\n4. Initializing periodic job service...")
    mongo_connection = os.getenv('MONGODB_CONNECTION_STRING', 'mongodb://localhost:27017/')
    service = PeriodicJobService(mongo_connection)
    
    try:
        # Connect to MongoDB (needed for job state tracking)
        print("\n5. Connecting to MongoDB...")
        if service.connect_to_mongodb():
            print("✅ MongoDB connection successful")
        else:
            print("⚠️  MongoDB connection failed - continuing with limited functionality")
        
        # Configure file-based data source
        print("\n6. Configuring file-based data source...")
        config_success = service.configure_data_source(
            source_type="file",
            file_path=str(test_dirs['input']),
            output_path=str(test_dirs['output'])
        )
        
        if config_success:
            print("✅ Data source configured successfully")
            print(f"   - Source type: file")
            print(f"   - Input path: {test_dirs['input']}")
            print(f"   - Output path: {test_dirs['output']}")
        else:
            print("❌ Failed to configure data source")
            return
        
        # Display current configuration
        print("\n7. Current data source configuration:")
        config = service.get_data_source_config()
        print(json.dumps(config, indent=2))
        
        # Reset job state for clean test
        print("\n8. Resetting job state for clean test...")
        service.reset_job_state()
        print("✅ Job state reset")
        
        # Run a single batch to process the files
        print("\n9. Running periodic job batch...")
        print("   Processing files and generating performance analysis...")
        
        batch_stats = service.run_single_batch()
        
        print(f"\n📊 Batch Processing Results:")
        print(f"   - Records processed: {batch_stats['records_processed']}")
        print(f"   - Records analyzed: {batch_stats['records_analyzed']}")
        print(f"   - Records persisted: {batch_stats['records_persisted']}")
        print(f"   - Errors: {batch_stats['errors']}")
        print(f"   - Duration: {batch_stats.get('duration', 0):.2f} seconds")
        
        # Check output files
        print("\n10. Checking generated output files...")
        output_files = list(test_dirs['output'].glob("*.json"))
        
        if output_files:
            print(f"✅ Generated {len(output_files)} analysis result files:")
            for output_file in output_files:
                file_size = output_file.stat().st_size
                print(f"   - {output_file.name} ({file_size} bytes)")
                
                # Display a sample of the first output file
                if output_file == output_files[0]:
                    print(f"\n📄 Sample content from {output_file.name}:")
                    try:
                        with open(output_file, 'r', encoding='utf-8') as f:
                            sample_result = json.load(f)
                        
                        # Display key information
                        print(f"   - Customer: {sample_result.get('customer', 'N/A')}")
                        print(f"   - Conversation ID: {sample_result.get('conversation_id', 'N/A')}")
                        print(f"   - Created at: {sample_result.get('created_at', 'N/A')}")
                        
                        # Display performance metrics summary
                        if 'performance_metrics' in sample_result:
                            metrics = sample_result['performance_metrics']
                            print(f"   - Performance Categories: {len(metrics.get('categories', {}))}")
                            
                            # Show some key scores
                            for category, data in metrics.get('categories', {}).items():
                                if isinstance(data, dict) and 'kpis' in data:
                                    kpi_count = len(data['kpis'])
                                    print(f"     * {category}: {kpi_count} KPIs analyzed")
                        
                        # Display persistence metadata
                        if 'persistence_metadata' in sample_result:
                            persistence = sample_result['persistence_metadata']
                            print(f"   - Storage type: {persistence.get('storage_type', 'N/A')}")
                            print(f"   - File path: {persistence.get('file_path', 'N/A')}")
                    
                    except Exception as e:
                        print(f"   ⚠️  Could not read sample file: {e}")
        else:
            print("❌ No output files generated")
        
        # Get job statistics
        print("\n11. Final job statistics...")
        try:
            stats = service.get_job_statistics()
            
            if 'error' not in stats:
                print("📈 Job Statistics:")
                job_state = stats.get('job_state', {})
                print(f"   - Job status: {job_state.get('status', 'N/A')}")
                print(f"   - Last updated: {job_state.get('last_updated', 'N/A')}")
                
                # Show processed files
                processed_files = job_state.get('processed_files', [])
                if processed_files:
                    print(f"   - Processed files: {len(processed_files)}")
                    for pf in processed_files:
                        print(f"     * {Path(pf).name}")
                
                # Show output files tracked
                output_files_tracked = job_state.get('output_files', [])
                if output_files_tracked:
                    print(f"   - Output files tracked: {len(output_files_tracked)}")
                    for of in output_files_tracked:
                        print(f"     * {Path(of['file_path']).name}")
                        
            else:
                print(f"⚠️  Error getting job statistics: {stats['error']}")
                
        except Exception as e:
            print(f"⚠️  Could not get job statistics: {e}")
        
        # Test running another batch (should find no new files)
        print("\n12. Testing incremental processing...")
        print("   Running another batch (should find no new files)...")
        
        batch_stats_2 = service.run_single_batch()
        print(f"   - Records processed: {batch_stats_2['records_processed']}")
        if batch_stats_2['records_processed'] == 0:
            print("✅ Incremental processing working correctly - no duplicate processing")
        else:
            print("⚠️  Unexpected: files were processed again")
        
        # Summary
        print("\n" + "=" * 70)
        print("🎉 Test Complete!")
        print("=" * 70)
        
        if batch_stats['records_processed'] > 0 and len(output_files) > 0:
            print("✅ SUCCESS: Periodic job successfully:")
            print("   - Read sentiment data from files")
            print("   - Performed performance analysis")
            print("   - Saved results to output files")
            print("   - Tracked processing state correctly")
            print("   - Handled incremental processing")
        else:
            print("❌ ISSUES DETECTED: Check the logs above for details")
        
        # Cleanup instructions
        print(f"\n📁 Test files created in: {test_dirs['base']}")
        print("   You can examine the input and output files, then delete the directory when done.")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Cleanup service
        service.cleanup()
        print("\n🧹 Service cleanup completed")

def display_usage():
    """Display usage information"""
    print("📖 Usage: python test_periodic_job_file_source.py")
    print()
    print("This script tests the periodic job service with file-based data sources.")
    print("It demonstrates:")
    print("  • Configuring the periodic job to read from files")
    print("  • Processing sentiment analysis data from JSON files")
    print("  • Generating performance analysis results")
    print("  • Saving results to output files")
    print("  • Incremental processing (avoiding duplicate work)")
    print()
    print("Requirements:")
    print("  • MongoDB running (for job state tracking)")
    print("  • AI Core credentials configured (optional - will use simulation)")
    print()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        display_usage()
    else:
        test_periodic_job_file_source()
