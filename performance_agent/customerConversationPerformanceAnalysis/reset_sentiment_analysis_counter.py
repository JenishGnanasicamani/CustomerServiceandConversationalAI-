#!/usr/bin/env python3
"""
Reset Sentiment Analysis Processing Counter

This script resets the job state counter so that all records from the 
sentiment_analysis collection can be processed again by the periodic job service.
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

try:
    from pymongo import MongoClient
    from bson import ObjectId
    MONGODB_AVAILABLE = True
except ImportError as e:
    print(f"❌ MongoDB not available: {e}")
    print("   Please install pymongo: pip install pymongo")
    sys.exit(1)

class SentimentAnalysisCounterReset:
    """Class to reset the sentiment analysis processing counter"""
    
    def __init__(self, mongo_connection_string: str = None, db_name: str = "csai"):
        """
        Initialize the counter reset service
        
        Args:
            mongo_connection_string: MongoDB connection string
            db_name: Database name (default: csai)
        """
        self.mongo_connection_string = mongo_connection_string or os.getenv(
            'MONGODB_CONNECTION_STRING', 
            'mongodb://localhost:27017/'
        )
        self.db_name = db_name
        self.client = None
        self.db = None
        self.job_name = "conversation_performance_analysis"
        
    def connect_to_mongodb(self) -> bool:
        """Connect to MongoDB and initialize collections"""
        try:
            self.client = MongoClient(self.mongo_connection_string)
            self.db = self.client[self.db_name]
            
            # Test connection
            self.client.admin.command('ping')
            print(f"✅ Connected to MongoDB database: {self.db_name}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to connect to MongoDB: {e}")
            return False
    
    def analyze_current_state(self) -> dict:
        """Analyze the current processing state"""
        try:
            # Get collection references
            sentiment_collection = self.db['sentiment_analysis']
            job_state_collection = self.db['job_state']
            agentic_collection = self.db['agentic_analysis']
            
            # Get counts
            sentiment_count = sentiment_collection.count_documents({})
            agentic_count = agentic_collection.count_documents({})
            
            # Get job state
            job_state = job_state_collection.find_one({"job_name": self.job_name})
            
            # Get processing statistics
            analysis = {
                "sentiment_analysis_count": sentiment_count,
                "agentic_analysis_count": agentic_count,
                "job_state": job_state,
                "processed_records": 0,
                "remaining_records": sentiment_count
            }
            
            if job_state and job_state.get('last_processed_object_id'):
                # Calculate how many records have been processed
                try:
                    last_id = ObjectId(job_state['last_processed_object_id'])
                    processed_count = sentiment_collection.count_documents({"_id": {"$lte": last_id}})
                    remaining_count = sentiment_collection.count_documents({"_id": {"$gt": last_id}})
                    
                    analysis["processed_records"] = processed_count
                    analysis["remaining_records"] = remaining_count
                    
                except Exception as e:
                    print(f"⚠️  Warning: Could not calculate processed records: {e}")
            
            return analysis
            
        except Exception as e:
            print(f"❌ Error analyzing current state: {e}")
            return {}
    
    def reset_job_state(self, backup: bool = True) -> bool:
        """
        Reset the job state to process all records from the beginning
        
        Args:
            backup: Whether to backup the current job state before reset
            
        Returns:
            bool: True if reset was successful
        """
        try:
            job_state_collection = self.db['job_state']
            
            # Get current job state for backup
            current_state = job_state_collection.find_one({"job_name": self.job_name})
            
            if backup and current_state:
                # Create backup
                backup_data = {
                    **current_state,
                    "backup_timestamp": datetime.now().isoformat(),
                    "original_job_name": current_state["job_name"],
                    "job_name": f"{self.job_name}_backup_{int(datetime.now().timestamp())}"
                }
                
                job_state_collection.insert_one(backup_data)
                print(f"✅ Backup created with job_name: {backup_data['job_name']}")
            
            # Reset the job state
            result = job_state_collection.delete_one({"job_name": self.job_name})
            
            if result.deleted_count > 0:
                print(f"✅ Job state reset successfully. Deleted {result.deleted_count} record(s).")
                return True
            else:
                print(f"ℹ️  No existing job state found for '{self.job_name}'. Counter was already reset.")
                return True
                
        except Exception as e:
            print(f"❌ Error resetting job state: {e}")
            return False
    
    def verify_reset(self) -> bool:
        """Verify that the reset was successful"""
        try:
            job_state_collection = self.db['job_state']
            
            # Check if job state still exists
            job_state = job_state_collection.find_one({"job_name": self.job_name})
            
            if job_state is None:
                print("✅ Reset verification successful: No job state found")
                return True
            else:
                print("❌ Reset verification failed: Job state still exists")
                print(f"   Current state: {job_state}")
                return False
                
        except Exception as e:
            print(f"❌ Error verifying reset: {e}")
            return False
    
    def show_impact_summary(self, before_analysis: dict, after_reset: bool) -> None:
        """Show the impact of the reset operation"""
        print("\n" + "="*60)
        print("RESET IMPACT SUMMARY")
        print("="*60)
        
        sentiment_count = before_analysis.get("sentiment_analysis_count", 0)
        agentic_count = before_analysis.get("agentic_analysis_count", 0)
        processed_count = before_analysis.get("processed_records", 0)
        
        print(f"📊 Collection Counts:")
        print(f"   - sentiment_analysis records: {sentiment_count:,}")
        print(f"   - agentic_analysis records: {agentic_count:,}")
        
        if before_analysis.get("job_state"):
            job_state = before_analysis["job_state"]
            print(f"\n📝 Previous Job State:")
            print(f"   - Status: {job_state.get('status', 'N/A')}")
            print(f"   - Last processed ID: {job_state.get('last_processed_object_id', 'None')}")
            print(f"   - Last updated: {job_state.get('last_updated', 'N/A')}")
            print(f"   - Records processed: {processed_count:,}")
            print(f"   - Records remaining: {before_analysis.get('remaining_records', 0):,}")
        else:
            print(f"\n📝 Previous Job State: None (first run)")
        
        print(f"\n🔄 Reset Operation:")
        if after_reset:
            print(f"   ✅ Counter reset successful")
            print(f"   📈 Records to be processed: {sentiment_count:,}")
            print(f"   🎯 Processing will start from the beginning")
        else:
            print(f"   ❌ Counter reset failed")
        
        print(f"\n💡 Next Steps:")
        if after_reset:
            print(f"   1. Run the periodic job service: python run_periodic_job.py")
            print(f"   2. All {sentiment_count:,} records will be processed")
            print(f"   3. Results will be stored in agentic_analysis collection")
        else:
            print(f"   1. Check MongoDB connection and permissions")
            print(f"   2. Retry the reset operation")
    
    def run_reset(self, backup: bool = True, confirm: bool = True) -> bool:
        """
        Run the complete reset operation
        
        Args:
            backup: Whether to backup current state
            confirm: Whether to ask for user confirmation
            
        Returns:
            bool: True if reset was successful
        """
        print("🔄 SENTIMENT ANALYSIS COUNTER RESET")
        print("="*50)
        
        # Step 1: Connect to MongoDB
        print("\n1. Connecting to MongoDB...")
        if not self.connect_to_mongodb():
            return False
        
        # Step 2: Analyze current state
        print("\n2. Analyzing current processing state...")
        before_analysis = self.analyze_current_state()
        
        if not before_analysis:
            print("❌ Could not analyze current state")
            return False
        
        # Show current state
        sentiment_count = before_analysis.get("sentiment_analysis_count", 0)
        processed_count = before_analysis.get("processed_records", 0)
        remaining_count = before_analysis.get("remaining_records", 0)
        
        print(f"   📊 Found {sentiment_count:,} total records in sentiment_analysis")
        print(f"   ✅ Already processed: {processed_count:,} records")
        print(f"   ⏳ Remaining to process: {remaining_count:,} records")
        
        # Step 3: Confirmation
        if confirm:
            print(f"\n3. Confirmation required...")
            print(f"   ⚠️  This will reset the processing counter")
            print(f"   📈 All {sentiment_count:,} records will be reprocessed")
            if backup:
                print(f"   💾 Current state will be backed up")
            
            response = input(f"\n   Continue with reset? (y/N): ").strip().lower()
            if response not in ['y', 'yes']:
                print("   ❌ Reset cancelled by user")
                return False
        
        # Step 4: Reset operation
        print(f"\n4. Resetting job state counter...")
        reset_success = self.reset_job_state(backup=backup)
        
        # Step 5: Verify reset
        if reset_success:
            print(f"\n5. Verifying reset...")
            verify_success = self.verify_reset()
            reset_success = reset_success and verify_success
        
        # Step 6: Show impact summary
        self.show_impact_summary(before_analysis, reset_success)
        
        return reset_success
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            if self.client:
                self.client.close()
                print("📝 MongoDB connection closed")
        except Exception as e:
            print(f"⚠️  Error during cleanup: {e}")


def main():
    """Main function"""
    print("🚀 Sentiment Analysis Counter Reset Tool")
    print("=" * 50)
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Reset sentiment analysis processing counter")
    parser.add_argument("--no-backup", action="store_true", help="Skip backup of current state")
    parser.add_argument("--no-confirm", action="store_true", help="Skip confirmation prompt")
    parser.add_argument("--db-name", default="csai", help="Database name (default: csai)")
    parser.add_argument("--connection-string", help="MongoDB connection string")
    
    args = parser.parse_args()
    
    # Create reset service
    reset_service = SentimentAnalysisCounterReset(
        mongo_connection_string=args.connection_string,
        db_name=args.db_name
    )
    
    try:
        # Run the reset operation
        success = reset_service.run_reset(
            backup=not args.no_backup,
            confirm=not args.no_confirm
        )
        
        if success:
            print("\n🎉 Counter reset completed successfully!")
            print("   You can now run the periodic job to process all records.")
            return 0
        else:
            print("\n❌ Counter reset failed!")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1
    finally:
        reset_service.cleanup()


if __name__ == "__main__":
    sys.exit(main())
