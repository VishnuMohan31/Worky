"""create_chat_assistant_tables

Revision ID: a1b2c3d4e5f6
Revises: 038e046dcb19
Create Date: 2025-11-28 20:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '038e046dcb19'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create chat_messages table
    op.create_table(
        'chat_messages',
        sa.Column('id', sa.String(20), primary_key=True),
        sa.Column('session_id', sa.String(50), nullable=False, index=True),
        sa.Column('user_id', sa.String(20), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),  # "user" or "assistant"
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('intent_type', sa.String(50), nullable=True),
        sa.Column('entities', sa.JSON, nullable=True),
        sa.Column('actions', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)
    )
    
    # Create indexes for chat_messages
    op.create_index('idx_chat_messages_session', 'chat_messages', ['session_id'])
    op.create_index('idx_chat_messages_user', 'chat_messages', ['user_id'])
    op.create_index('idx_chat_messages_created', 'chat_messages', ['created_at'])
    
    # Create chat_audit_logs table
    op.create_table(
        'chat_audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('request_id', sa.String(50), nullable=False, unique=True, index=True),
        sa.Column('user_id', sa.String(20), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('client_id', sa.String(20), sa.ForeignKey('clients.id'), nullable=False),
        sa.Column('session_id', sa.String(50), nullable=False, index=True),
        sa.Column('query', sa.Text, nullable=False),  # PII masked
        sa.Column('intent_type', sa.String(50), nullable=True),
        sa.Column('entities_accessed', sa.JSON, nullable=True),
        sa.Column('action_performed', sa.String(100), nullable=True),
        sa.Column('action_result', sa.String(20), nullable=True),  # "success", "failed", "denied"
        sa.Column('response_summary', sa.Text, nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False, index=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.Text, nullable=True)
    )
    
    # Create indexes for chat_audit_logs
    op.create_index('idx_chat_audit_logs_user', 'chat_audit_logs', ['user_id'])
    op.create_index('idx_chat_audit_logs_client', 'chat_audit_logs', ['client_id'])
    op.create_index('idx_chat_audit_logs_session', 'chat_audit_logs', ['session_id'])
    op.create_index('idx_chat_audit_logs_timestamp', 'chat_audit_logs', ['timestamp'])
    
    # Create reminders table
    op.create_table(
        'reminders',
        sa.Column('id', sa.String(20), primary_key=True),
        sa.Column('user_id', sa.String(20), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('entity_type', sa.String(50), nullable=False),  # "task", "bug", "project"
        sa.Column('entity_id', sa.String(20), nullable=False),
        sa.Column('message', sa.Text, nullable=True),
        sa.Column('remind_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_sent', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('created_via', sa.String(20), nullable=False, server_default='chat'),  # "chat", "ui", "api"
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)
    )
    
    # Create indexes for reminders
    op.create_index('idx_reminders_user', 'reminders', ['user_id'])
    op.create_index('idx_reminders_remind_at', 'reminders', ['remind_at'])
    op.create_index('idx_reminders_is_sent', 'reminders', ['is_sent'])
    op.create_index('idx_reminders_entity', 'reminders', ['entity_type', 'entity_id'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop reminders table and indexes
    op.drop_index('idx_reminders_entity', table_name='reminders')
    op.drop_index('idx_reminders_is_sent', table_name='reminders')
    op.drop_index('idx_reminders_remind_at', table_name='reminders')
    op.drop_index('idx_reminders_user', table_name='reminders')
    op.drop_table('reminders')
    
    # Drop chat_audit_logs table and indexes
    op.drop_index('idx_chat_audit_logs_timestamp', table_name='chat_audit_logs')
    op.drop_index('idx_chat_audit_logs_session', table_name='chat_audit_logs')
    op.drop_index('idx_chat_audit_logs_client', table_name='chat_audit_logs')
    op.drop_index('idx_chat_audit_logs_user', table_name='chat_audit_logs')
    op.drop_table('chat_audit_logs')
    
    # Drop chat_messages table and indexes
    op.drop_index('idx_chat_messages_created', table_name='chat_messages')
    op.drop_index('idx_chat_messages_user', table_name='chat_messages')
    op.drop_index('idx_chat_messages_session', table_name='chat_messages')
    op.drop_table('chat_messages')
