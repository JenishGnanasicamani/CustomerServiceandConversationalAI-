#!/usr/bin/env python3
"""
Run Periodic Job for Customer Conversation Performance Analysis
Main script to start the periodic job service that processes sentiment analysis data
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from src.periodic_job_service import PeriodicJobService


def main():
    """Main function to run the periodic job service"""
    
    parser = argparse.ArgumentParser(description="Run Customer Conversation Performance Analysis Periodic Job")
    parser.add_argument("--mongo-uri", type=str, 
                       default=os.getenv('MONGODB_CONNECTION_STRING', 'mongodb://localhost:27017/'),
                       help="MongoDB connection string")
    parser.add_argument("--db-name", type=str, default="csai",
                       help="Database name (default: csai)")
    parser.add_argument("--interval", type=int, default=5,
                       help="Interval between job runs in minutes (default: 5)")
    parser.add_argument("--batch-size", type=int, default=50,
                       help="Batch size for processing records (default: 50)")
    parser.add_argument("--max-iterations", type=int, default=None,
                       help="Maximum iterations to run (default: infinite)")
    parser.add_argument("--single-batch", action="store_true",
                       help="Run only a single batch instead of continuous job")
    parser.add_argument("--reset-state", action="store_true",
                       help="Reset job state before starting")
    parser.add_argument("--stats-only", action="store_true",
                       help="Show job statistics only (don't run job)")
    parser.add_argument("--log-level", type=str, default="INFO",
                       choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                       help="Logging level (default: INFO)")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    
    # Initialize service
    logger.info("Initializing Periodic Job Service...")
    service = PeriodicJobService(args.mongo_uri, args.db_name)
    service.batch_size = args.batch_size
    
    try:
        # Connect to MongoDB
        if not service.connect_to_mongodb():
            logger.error("Failed to connect to MongoDB")
            return 1
        
        # Reset job state if requested
        if args.reset_state:
            logger.info("Resetting job state...")
            service.reset_job_state()
        
        # Show statistics if requested
        if args.stats_only:
            logger.info("Getting job statistics...")
            stats = service.get_job_statistics()
            print("\n" + "="*80)
            print("JOB STATISTICS")
            print("="*80)
            
            if "error" in stats:
                print(f"Error getting stats: {stats['error']}")
            else:
                job_state = stats.get("job_state")
                if job_state:
                    print(f"Job Status: {job_state.get('status', 'Unknown')}")
                    print(f"Last Updated: {job_state.get('last_updated', 'Unknown')}")
                    print(f"Last Processed ID: {job_state.get('last_processed_object_id', 'None')}")
                else:
                    print("Job Status: Not started")
                
                print(f"Agentic Analysis Records: {stats.get('agentic_analysis_count', 0)}")
                print(f"Latest Results: {stats.get('latest_results_count', 0)}")
                
                if stats.get('latest_results'):
                    print("\nRecent Analysis Results:")
                    for result in stats['latest_results'][:5]:
                        print(f"  • {result.get('conversation_id', 'Unknown')} - "
                              f"{result.get('processed_timestamp', 'Unknown')} - "
                              f"{result.get('model_used', 'Unknown')}")
            
            return 0
        
        # Run job
        if args.single_batch:
            logger.info("Running single batch...")
            batch_stats = service.run_single_batch()
            
            print("\n" + "="*80)
            print("BATCH RESULTS")
            print("="*80)
            print(f"Records Processed: {batch_stats['records_processed']}")
            print(f"Records Analyzed: {batch_stats['records_analyzed']}")
            print(f"Records Persisted: {batch_stats['records_persisted']}")
            print(f"Errors: {batch_stats['errors']}")
            print(f"Duration: {batch_stats.get('duration', 0):.2f} seconds")
            print(f"Last Processed ID: {batch_stats.get('last_processed_id', 'None')}")
            
        else:
            logger.info(f"Starting continuous job (interval: {args.interval} minutes, max iterations: {args.max_iterations})")
            service.run_continuous_job(args.interval, args.max_iterations)
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("Job interrupted by user")
        return 0
    except Exception as e:
        logger.error(f"Error running periodic job: {e}")
        return 1
    finally:
        service.cleanup()


if __name__ == "__main__":
    sys.exit(main())
