from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Tuple
from datetime import datetime, timedelta
import re
import json
from app.crud.base import CRUDBase
from app.models.comment import BugComment, TestCaseComment
from app.schemas.comment import CommentCreate, CommentUpdate


class CRUDComment:
    """
    CRUD operations for both BugComment and TestCaseComment.
    This class handles comments for both entity types.
    """
    
    # Edit time window in minutes
    EDIT_TIME_WINDOW = 15
    
    async def get_by_entity(
        self,
        db: AsyncSession,
        *,
        entity_type: str,
        entity_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[BugComment | TestCaseComment]:
        """
        Get comments for a specific entity (bug or test case).
        
        Args:
            db: Database session
            entity_type: Type of entity ('bug' or 'test_case')
            entity_id: Entity ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of comments ordered by creation date (oldest first)
        """
        if entity_type == "bug":
            query = select(BugComment).where(
                BugComment.bug_id == entity_id,
                BugComment.is_deleted == False
            ).order_by(BugComment.created_at.asc())
        elif entity_type == "test_case":
            query = select(TestCaseComment).where(
                TestCaseComment.test_case_id == entity_id,
                TestCaseComment.is_deleted == False
            ).order_by(TestCaseComment.created_at.asc())
        else:
            raise ValueError(f"Invalid entity_type: {entity_type}. Must be 'bug' or 'test_case'")
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get(
        self,
        db: AsyncSession,
        *,
        comment_id: str,
        entity_type: str
    ) -> Optional[BugComment | TestCaseComment]:
        """
        Get a single comment by ID.
        
        Args:
            db: Database session
            comment_id: Comment ID
            entity_type: Type of entity ('bug' or 'test_case')
            
        Returns:
            Comment or None
        """
        if entity_type == "bug":
            query = select(BugComment).where(
                BugComment.id == comment_id,
                BugComment.is_deleted == False
            )
        elif entity_type == "test_case":
            query = select(TestCaseComment).where(
                TestCaseComment.id == comment_id,
                TestCaseComment.is_deleted == False
            )
        else:
            raise ValueError(f"Invalid entity_type: {entity_type}")
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def create(
        self,
        db: AsyncSession,
        *,
        entity_type: str,
        entity_id: str,
        comment_in: CommentCreate,
        author_id: str
    ) -> BugComment | TestCaseComment:
        """
        Create a new comment.
        
        Args:
            db: Database session
            entity_type: Type of entity ('bug' or 'test_case')
            entity_id: Entity ID
            comment_in: Comment data
            author_id: Author user ID
            
        Returns:
            Created comment
        """
        # Extract mentions from comment text
        mentioned_users = self.extract_mentions(comment_in.comment_text)
        
        # Merge with explicitly provided mentions
        if comment_in.mentioned_users:
            try:
                explicit_mentions = json.loads(comment_in.mentioned_users)
                mentioned_users = list(set(mentioned_users + explicit_mentions))
            except json.JSONDecodeError:
                pass
        
        # Convert to JSON string
        mentioned_users_json = json.dumps(mentioned_users) if mentioned_users else None
        
        if entity_type == "bug":
            comment = BugComment(
                bug_id=entity_id,
                comment_text=comment_in.comment_text,
                author_id=author_id,
                mentioned_users=mentioned_users_json,
                attachments=comment_in.attachments
            )
        elif entity_type == "test_case":
            comment = TestCaseComment(
                test_case_id=entity_id,
                comment_text=comment_in.comment_text,
                author_id=author_id,
                mentioned_users=mentioned_users_json,
                attachments=comment_in.attachments
            )
        else:
            raise ValueError(f"Invalid entity_type: {entity_type}")
        
        db.add(comment)
        await db.commit()
        await db.refresh(comment)
        return comment
    
    async def update(
        self,
        db: AsyncSession,
        *,
        comment_id: str,
        entity_type: str,
        comment_in: CommentUpdate,
        user_id: str
    ) -> Tuple[Optional[BugComment | TestCaseComment], str]:
        """
        Update a comment with edit time window validation.
        
        Args:
            db: Database session
            comment_id: Comment ID
            entity_type: Type of entity ('bug' or 'test_case')
            comment_in: Updated comment data
            user_id: User making the update
            
        Returns:
            Tuple of (updated_comment, error_message)
        """
        comment = await self.get(db, comment_id=comment_id, entity_type=entity_type)
        
        if not comment:
            return None, f"Comment with id {comment_id} not found"
        
        # Validate user is the author
        if comment.author_id != user_id:
            return None, "Only the comment author can edit the comment"
        
        # Validate edit time window
        is_valid, error_msg = self.validate_edit_time_window(comment.created_at)
        if not is_valid:
            return None, error_msg
        
        # Update comment
        if comment_in.comment_text:
            comment.comment_text = comment_in.comment_text
            
            # Re-extract mentions from updated text
            mentioned_users = self.extract_mentions(comment_in.comment_text)
            comment.mentioned_users = json.dumps(mentioned_users) if mentioned_users else None
        
        if comment_in.attachments is not None:
            comment.attachments = comment_in.attachments
        
        comment.is_edited = True
        comment.edited_at = datetime.utcnow()
        
        db.add(comment)
        await db.commit()
        await db.refresh(comment)
        
        return comment, ""
    
    async def delete(
        self,
        db: AsyncSession,
        *,
        comment_id: str,
        entity_type: str,
        user_id: str
    ) -> Tuple[bool, str]:
        """
        Soft delete a comment.
        
        Args:
            db: Database session
            comment_id: Comment ID
            entity_type: Type of entity ('bug' or 'test_case')
            user_id: User making the deletion
            
        Returns:
            Tuple of (success, error_message)
        """
        comment = await self.get(db, comment_id=comment_id, entity_type=entity_type)
        
        if not comment:
            return False, f"Comment with id {comment_id} not found"
        
        # Validate user is the author
        if comment.author_id != user_id:
            return False, "Only the comment author can delete the comment"
        
        # Soft delete
        comment.is_deleted = True
        
        db.add(comment)
        await db.commit()
        
        return True, ""
    
    def extract_mentions(self, text: str) -> List[str]:
        """
        Extract @mentions from comment text.
        
        Args:
            text: Comment text
            
        Returns:
            List of mentioned user IDs or usernames
        """
        # Pattern to match @username or @user_id
        # Assumes mentions are in format @username or @user_id
        pattern = r'@(\w+)'
        matches = re.findall(pattern, text)
        return matches
    
    def validate_edit_time_window(
        self,
        created_at: datetime
    ) -> Tuple[bool, str]:
        """
        Validate that the comment is within the edit time window.
        
        Args:
            created_at: Comment creation timestamp
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        now = datetime.utcnow()
        time_diff = now - created_at
        
        if time_diff > timedelta(minutes=self.EDIT_TIME_WINDOW):
            return False, f"Comments can only be edited within {self.EDIT_TIME_WINDOW} minutes of posting"
        
        return True, ""
    
    async def count_by_entity(
        self,
        db: AsyncSession,
        *,
        entity_type: str,
        entity_id: str
    ) -> int:
        """
        Count comments for a specific entity.
        
        Args:
            db: Database session
            entity_type: Type of entity ('bug' or 'test_case')
            entity_id: Entity ID
            
        Returns:
            Count of comments
        """
        from sqlalchemy import func
        
        if entity_type == "bug":
            query = select(func.count(BugComment.id)).where(
                BugComment.bug_id == entity_id,
                BugComment.is_deleted == False
            )
        elif entity_type == "test_case":
            query = select(func.count(TestCaseComment.id)).where(
                TestCaseComment.test_case_id == entity_id,
                TestCaseComment.is_deleted == False
            )
        else:
            raise ValueError(f"Invalid entity_type: {entity_type}")
        
        result = await db.execute(query)
        return result.scalar_one()


class CRUDBugComment(CRUDBase[BugComment, CommentCreate, CommentUpdate]):
    """CRUD operations specifically for BugComment"""
    
    async def get_by_bug(
        self,
        db: AsyncSession,
        *,
        bug_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[BugComment]:
        """Get all comments for a bug"""
        query = select(BugComment).where(
            BugComment.bug_id == bug_id,
            BugComment.is_deleted == False
        ).order_by(BugComment.created_at.asc())
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()


class CRUDTestCaseComment(CRUDBase[TestCaseComment, CommentCreate, CommentUpdate]):
    """CRUD operations specifically for TestCaseComment"""
    
    async def get_by_test_case(
        self,
        db: AsyncSession,
        *,
        test_case_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[TestCaseComment]:
        """Get all comments for a test case"""
        query = select(TestCaseComment).where(
            TestCaseComment.test_case_id == test_case_id,
            TestCaseComment.is_deleted == False
        ).order_by(TestCaseComment.created_at.asc())
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()


class CRUDAttachment:
    """CRUD operations for bug attachments"""
    
    async def get_by_bug(
        self,
        db: AsyncSession,
        *,
        bug_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List:
        """
        Get all attachments for a bug.
        
        Args:
            db: Database session
            bug_id: Bug ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of attachments
        """
        from app.models.comment import BugAttachment
        
        query = select(BugAttachment).where(
            BugAttachment.bug_id == bug_id,
            BugAttachment.is_deleted == False
        ).order_by(BugAttachment.uploaded_at.desc())
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get(
        self,
        db: AsyncSession,
        *,
        attachment_id: str
    ) -> Optional:
        """
        Get a single attachment by ID.
        
        Args:
            db: Database session
            attachment_id: Attachment ID
            
        Returns:
            Attachment or None
        """
        from app.models.comment import BugAttachment
        
        query = select(BugAttachment).where(
            BugAttachment.id == attachment_id,
            BugAttachment.is_deleted == False
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def create(
        self,
        db: AsyncSession,
        *,
        bug_id: str,
        file_name: str,
        file_path: str,
        file_type: str,
        file_size: int,
        uploaded_by: str
    ):
        """
        Create a new attachment.
        
        Args:
            db: Database session
            bug_id: Bug ID
            file_name: Name of the file
            file_path: Path to the file
            file_type: MIME type of the file
            file_size: Size of the file in bytes
            uploaded_by: User ID of the uploader
            
        Returns:
            Created attachment
        """
        from app.models.comment import BugAttachment
        
        attachment = BugAttachment(
            bug_id=bug_id,
            file_name=file_name,
            file_path=file_path,
            file_type=file_type,
            file_size=file_size,
            uploaded_by=uploaded_by
        )
        
        db.add(attachment)
        await db.commit()
        await db.refresh(attachment)
        return attachment
    
    async def delete(
        self,
        db: AsyncSession,
        *,
        attachment_id: str,
        user_id: str
    ) -> Tuple[bool, str]:
        """
        Soft delete an attachment.
        
        Args:
            db: Database session
            attachment_id: Attachment ID
            user_id: User making the deletion
            
        Returns:
            Tuple of (success, error_message)
        """
        attachment = await self.get(db, attachment_id=attachment_id)
        
        if not attachment:
            return False, f"Attachment with id {attachment_id} not found"
        
        # Validate user is the uploader or has permission
        if attachment.uploaded_by != user_id:
            # TODO: Add admin/permission check
            return False, "Only the uploader can delete the attachment"
        
        # Soft delete
        attachment.is_deleted = True
        
        db.add(attachment)
        await db.commit()
        
        return True, ""
    
    async def count_by_bug(
        self,
        db: AsyncSession,
        *,
        bug_id: str
    ) -> int:
        """
        Count attachments for a bug.
        
        Args:
            db: Database session
            bug_id: Bug ID
            
        Returns:
            Count of attachments
        """
        from app.models.comment import BugAttachment
        from sqlalchemy import func
        
        query = select(func.count(BugAttachment.id)).where(
            BugAttachment.bug_id == bug_id,
            BugAttachment.is_deleted == False
        )
        result = await db.execute(query)
        return result.scalar_one()


# Create instances
comment = CRUDComment()
bug_comment = CRUDBugComment(BugComment)
test_case_comment = CRUDTestCaseComment(TestCaseComment)
attachment = CRUDAttachment()
