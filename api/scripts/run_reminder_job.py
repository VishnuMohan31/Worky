#!/usr/bin/env python3
"""
CLI script to run the reminder background job.

Usage:
    python run_reminder_job.py [--interval MINUTES]

Options:
    --interval MINUTES    Check interval in minutes (default: 5)
"""
import asyncio
import argparse
import signal
import sys
from app.services.reminder_background_job import reminder_background_job


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    print("\nShutting down reminder background job...")
    reminder_background_job.stop()
    sys.exit(0)


async def main(interval_minutes: int = 5):
    """Main entry point for the reminder background job"""
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Initialize the job
        await reminder_background_job.initialize()
        
        # Run the job periodically
        await reminder_background_job.run_periodically(interval_minutes=interval_minutes)
        
    except Exception as e:
        print(f"Error running reminder background job: {e}")
        sys.exit(1)
    finally:
        # Clean up
        await reminder_background_job.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run the reminder background job to process pending reminders"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=5,
        help="Check interval in minutes (default: 5)"
    )
    
    args = parser.parse_args()
    
    print(f"Starting reminder background job (checking every {args.interval} minutes)...")
    print("Press Ctrl+C to stop")
    
    asyncio.run(main(interval_minutes=args.interval))
