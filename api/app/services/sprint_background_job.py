"""
Background job service for automatic sprint generation.
Ensures at least 6 future sprints exist for all active projects.
"""
import asyncio
from datetime import date
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select
from app.core.config import settings
from app.models.hierarchy import Project, Program
from app.models.sprint import Sprint
from app.services.sprint_service import SprintService
from app.core.logging import StructuredLogger

logger = StructuredLogger(__name__)


class SprintBackgroundJob:
    """Background job to ensure sprints are generated for all projects"""
    
    def __init__(self):
        self.running = False
        self.engine = None
        self.session_factory = None
    
    async def initialize(self):
        """Initialize database connection"""
        from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
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
        logger.info("Sprint background job initialized")
    
    async def close(self):
        """Close database connection"""
        if self.engine:
            await self.engine.dispose()
        logger.info("Sprint background job closed")
    
    async def ensure_sprints_for_all_projects(self):
        """Ensure all active projects have at least 6 future sprints"""
        if not self.session_factory:
            await self.initialize()
        
        async with self.session_factory() as db:
            try:
                # Get all active projects
                result = await db.execute(
                    select(Project)
                    .join(Program)
                    .where(Project.is_deleted == False)
                )
                projects = result.scalars().all()
                
                logger.info(f"Checking sprints for {len(projects)} projects")
                
                for project in projects:
                    try:
                        # Ensure sprints exist for this project (using project-level config)
                        await SprintService.ensure_future_sprints(
                            db=db,
                            project_id=project.id,
                            min_sprints=6
                        )
                        
                        logger.debug(f"Ensured sprints for project {project.id}")
                    except Exception as e:
                        logger.error(
                            f"Error ensuring sprints for project {project.id}: {str(e)}",
                            exc_info=True
                        )
                        continue
                
                logger.info("Sprint generation check completed")
            except Exception as e:
                logger.error(f"Error in sprint generation job: {str(e)}", exc_info=True)
    
    async def run_periodically(self, interval_minutes: int = 60):
        """Run the sprint generation job periodically"""
        self.running = True
        logger.info(f"Sprint background job started (runs every {interval_minutes} minutes)")
        
        while self.running:
            try:
                await self.ensure_sprints_for_all_projects()
            except Exception as e:
                logger.error(f"Error in periodic sprint job: {str(e)}", exc_info=True)
            
            # Wait for the specified interval
            await asyncio.sleep(interval_minutes * 60)
    
    def stop(self):
        """Stop the background job"""
        self.running = False
        logger.info("Sprint background job stopped")


# Global instance
sprint_background_job = SprintBackgroundJob()

