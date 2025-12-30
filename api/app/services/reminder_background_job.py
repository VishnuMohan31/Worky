"""
Background job service for processing pending reminders.
Checks for due reminders and sends notifications to users.
"""
import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.core.config import settings
from app.crud.crud_reminder import reminder as reminder_crud
from app.services.notification_service import NotificationService
from app.core.logging import StructuredLogger

logger = StructuredLogger(__name__)


class ReminderBackgroundJob:
    """Background job to process pending reminders"""
    
    def __init__(self):
        self.running = False
        self.engine = None
        self.session_factory = None
    
    async def initialize(self):
        """Initialize database connection"""
        self.engine = create_async_engine(
            settings.database_url,
            echo=False,
            pool_pre_ping=True
        )
        self.session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        logger.info("Reminder background job initialized")
    
    async def close(self):
        """Close database connection"""
        if self.engine:
            await self.engine.dispose()
        logger.info("Reminder background job closed")
    
    async def process_pending_reminders(self):
        """Process all pending reminders that are due"""
        if not self.session_factory:
            await self.initialize()
        
        async with self.session_factory() as db:
            try:
                # Process pending reminders using the notification service
                processed_count = await NotificationService.process_pending_reminders(
                    db=db,
                    reminder_crud=reminder_crud
                )
                
                if processed_count > 0:
                    logger.info(
                        f"Processed {processed_count} pending reminders",
                        processed_count=processed_count,
                        timestamp=datetime.now().isoformat()
                    )
                
                return processed_count
                
            except Exception as e:
                logger.error(
                    f"Error processing pending reminders: {str(e)}",
                    exc_info=True
                )
                return 0
    
    async def run_periodically(self, interval_minutes: int = 5):
        """
        Run the reminder processing job periodically.
        
        Args:
            interval_minutes: How often to check for pending reminders (default: 5 minutes)
        """
        self.running = True
        logger.info(
            f"Reminder background job started (runs every {interval_minutes} minutes)"
        )
        
        while self.running:
            try:
                await self.process_pending_reminders()
            except Exception as e:
                logger.error(
                    f"Error in periodic reminder job: {str(e)}",
                    exc_info=True
                )
            
            # Wait for the specified interval
            await asyncio.sleep(interval_minutes * 60)
    
    def stop(self):
        """Stop the background job"""
        self.running = False
        logger.info("Reminder background job stopped")


# Global instance
reminder_background_job = ReminderBackgroundJob()
