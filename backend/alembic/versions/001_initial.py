"""Initial migration

Revision ID: 001_initial
Revises:
Create Date: 2026-03-23
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Clients
    op.create_table(
        'clients',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('multilogin_profile_group', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )

    # Campaigns
    op.create_table(
        'campaigns',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('client_id', UUID(as_uuid=True), sa.ForeignKey('clients.id'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('target_url', sa.Text, nullable=False),
        sa.Column('excel_file_path', sa.String(500), nullable=True),
        sa.Column('excel_data', sa.JSON, nullable=True),
        sa.Column('duration_days', sa.Integer, default=30),
        sa.Column('start_date', sa.Date, nullable=False),
        sa.Column('end_date', sa.Date, nullable=False),
        sa.Column('status', sa.Enum('active', 'paused', 'completed', name='campaignstatus'), default='active'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )

    # Jobs
    op.create_table(
        'jobs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('campaign_id', UUID(as_uuid=True), sa.ForeignKey('campaigns.id'), nullable=False),
        sa.Column('scheduled_time', sa.DateTime, nullable=False),
        sa.Column('started_at', sa.DateTime, nullable=True),
        sa.Column('completed_at', sa.DateTime, nullable=True),
        sa.Column('status', sa.Enum('pending', 'queued', 'running', 'success', 'failed', 'retrying', name='jobstatus'), default='pending'),
        sa.Column('retry_count', sa.Integer, default=0),
        sa.Column('entry_data', sa.JSON, nullable=True),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )

    # Logs
    op.create_table(
        'logs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('job_id', UUID(as_uuid=True), sa.ForeignKey('jobs.id'), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('message', sa.Text, nullable=True),
        sa.Column('error_trace', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )

    # Indexes
    op.create_index('ix_jobs_campaign_id', 'jobs', ['campaign_id'])
    op.create_index('ix_jobs_scheduled_time', 'jobs', ['scheduled_time'])
    op.create_index('ix_jobs_status', 'jobs', ['status'])
    op.create_index('ix_logs_job_id', 'logs', ['job_id'])
    op.create_index('ix_campaigns_client_id', 'campaigns', ['client_id'])
    op.create_index('ix_campaigns_status', 'campaigns', ['status'])


def downgrade() -> None:
    op.drop_table('logs')
    op.drop_table('jobs')
    op.drop_table('campaigns')
    op.drop_table('clients')
    op.execute("DROP TYPE IF EXISTS campaignstatus")
    op.execute("DROP TYPE IF EXISTS jobstatus")
