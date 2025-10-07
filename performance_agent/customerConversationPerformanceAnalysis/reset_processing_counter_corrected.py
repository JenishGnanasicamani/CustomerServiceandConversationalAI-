#!/usr/bin/env python3
"""
Reset Processing Counter for Sentiment Analysis Collections

This script resets the job state counter so that all records from the 
sentiment analysis collections can be processed again by the periodic job service.
Updated to handle the correct collection name: 'sentimental_analysis'
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

class ProcessingCounterReset:
    """Class to reset the processing counter for various collections"""
    
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
    
    def show_available_collections(self) -> dict:
        """Show available collections with record counts"""
        try:
            collections_info = {}
            
            # Key collections to check
            key_collections = [
                'sentimental_analysis',  # Correct name!
                'sentiment_analysis',    # Check if this exists too
                'conversation_set',
                'messages',
                'Testing_Vivek',
                'Capstone Sample',
                'agentic_analysis',
                'job_state'
            ]
            
            print("📊 Available Collections with Data:")
            print("-" * 50)
            
            for collection_name in key_collections:
                try:
                    if collection_name in self.db.list_collection_names():
                        count = self.db[collection_name].count_documents({})
                        collections_info[collection_name] = count
                        
                        if count > 0:
                            # Get a sample document to show structure
                            sample = self.db[collection_name].find_one()
                            fields = list(sample.keys()) if sample else []
                            
                            print(f"✅ {collection_name}: {count:,} documents")
                            print(f"   Sample fields: {fields[:8]}{'...' if len(fields) > 8 else ''}")
                        else:
                            print(f"⚪ {collection_name}: {count} documents (empty)")
                    
                except Exception as e:
                    print(f"❌ Error checking {collection_name}: {e}")
            
            return collections_info
            
        except Exception as e:
            print(f"❌ Error listing collections: {e}")
            return {}
    
    def analyze_current_state(self, source_collection: str = "sentimental_analysis") -> dict:
        """Analyze the current processing state"""
        try:
            # Get collection references
            source_coll = self.db[source_collection]
            job_state_collection = self.db['job_state']
            agentic_collection = self.db['agentic_analysis']
            
            # Get counts
            source_count = source_coll.count_documents({})
            agentic_count = agentic_collection.count_documents({})
            
            # Get job state
            job_state = job_state_collection.find_one({"job_name": self.job_name})
            
            # Get processing statistics
            analysis = {
                "source_collection": source_collection,
                "source_count": source_count,
                "agentic_analysis_count": agentic_count,
                "job_state": job_state,
                "processed_records": 0,
                "remaining_records": source_count
            }
            
            if job_state and job_state.get('last_processed_object_id'):
                # Calculate how many records have been processed
                try:
                    last_id = ObjectId(job_state['last_processed_object_id'])
                    processed_count = source_coll.count_documents({"_id": {"$lte": last_id}})
                    remaining_count = source_coll.count_documents({"_id": {"$gt": last_id}})
                    
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
                # Create backup with a unique name to avoid duplicates
                backup_name = f"{self.job_name}_backup_{int(datetime.now().timestamp())}"
                backup_data = {
                    **current_state,
                    "_id": ObjectId(),  # Generate new ObjectId for backup
                    "backup_timestamp": datetime.now().isoformat(),
                    "original_job_name": current_state["job_name"],
                    "job_name": backup_name
                }
                
                # Remove the original _id to avoid conflicts
                backup_data.pop('_id', None)
                
                job_state_collection.insert_one(backup_data)
                print(f"✅ Backup created with job_name: {backup_name}")
            
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
        
        source_collection = before_analysis.get("source_collection", "unknown")
        source_count = before_analysis.get("source_count", 0)
        agentic_count = before_analysis.get("agentic_analysis_count", 0)
        processed_count = before_analysis.get("processed_records", 0)
        
        print(f"📊 Collection Counts:")
        print(f"   - {source_collection} records: {source_count:,}")
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
            print(f"   📈 Records to be processed: {source_count:,}")
            print(f"   🎯 Processing will start from the beginning")
        else:
            print(f"   ❌ Counter reset failed")
        
        print(f"\n💡 Next Steps:")
        if after_reset and source_count > 0:
            print(f"   1. Run the periodic job service: python run_periodic_job.py")
            print(f"   2. All {source_count:,} records from '{source_collection}' will be processed")
            print(f"   3. Results will be stored in agentic_analysis collection")
        elif after_reset and source_count == 0:
            print(f"   1. No records found in '{source_collection}' collection")
            print(f"   2. Consider using a different source collection")
            print(f"   3. Check if data exists in other collections")
        else:
            print(f"   1. Check MongoDB connection and permissions")
            print(f"   2. Retry the reset operation")
    
    def run_reset(self, source_collection: str = "sentimental_analysis", 
                  backup: bool = True, confirm: bool = True) -> bool:
        """
        Run the complete reset operation
        
        Args:
            source_collection: Source collection name
            backup: Whether to backup current state
            confirm: Whether to ask for user confirmation
            
        Returns:
            bool: True if reset was successful
        """
        print("🔄 PROCESSING COUNTER RESET")
        print("="*50)
        
        # Step 1: Connect to MongoDB
        print("\n1. Connecting to MongoDB...")
        if not self.connect_to_mongodb():
            return False
        
        # Step 2: Show available collections
        print("\n2. Showing available collections...")
        collections_info = self.show_available_collections()
        
        # Step 3: Analyze current state
        print(f"\n3. Analyzing current processing state for '{source_collection}'...")
        before_analysis = self.analyze_current_state(source_collection)
        
        if not before_analysis:
            print("❌ Could not analyze current state")
            return False
        
        # Show current state
        source_count = before_analysis.get("source_count", 0)
        processed_count = before_analysis.get("processed_records", 0)
        remaining_count = before_analysis.get("remaining_records", 0)
        
        print(f"   📊 Found {source_count:,} total records in '{source_collection}'")
        print(f"   ✅ Already processed: {processed_count:,} records")
        print(f"   ⏳ Remaining to process: {remaining_count:,} records")
        
        # Step 4: Confirmation
        if confirm:
            print(f"\n4. Confirmation required...")
            print(f"   ⚠️  This will reset the processing counter")
            print(f"   📈 All {source_count:,} records will be reprocessed")
            print(f"   🎯 Source collection: '{source_collection}'")
            if backup:
                print(f"   💾 Current state will be backed up")
            
            response = input(f"\n   Continue with reset? (y/N): ").strip().lower()
            if response not in ['y', 'yes']:
                print("   ❌ Reset cancelled by user")
                return False
        
        # Step 5: Reset operation
        print(f"\n5. Resetting job state counter...")
        reset_success = self.reset_job_state(backup=backup)
        
        # Step 6: Verify reset
        if reset_success:
            print(f"\n6. Verifying reset...")
            verify_success = self.verify_reset()
            reset_success = reset_success and verify_success
        
        # Step 7: Show impact summary
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
    print("🚀 Processing Counter Reset Tool (Corrected)")
    print("=" * 50)
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Reset processing counter for sentiment analysis")
    parser.add_argument("--collection", default="sentimental_analysis", 
                       help="Source collection name (default: sentimental_analysis)")
    parser.add_argument("--no-backup", action="store_true", help="Skip backup of current state")
    parser.add_argument("--no-confirm", action="store_true", help="Skip confirmation prompt")
    parser.add_argument("--db-name", default="csai", help="Database name (default: csai)")
    parser.add_argument("--connection-string", help="MongoDB connection string")
    
    args = parser.parse_args()
    
    # Create reset service
    reset_service = ProcessingCounterReset(
        mongo_connection_string=args.connection_string,
        db_name=args.db_name
    )
    
    try:
        # Run the reset operation
        success = reset_service.run_reset(
            source_collection=args.collection,
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
