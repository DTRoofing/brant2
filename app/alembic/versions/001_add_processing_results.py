"""Add processing results table

Revision ID: 001_add_processing_results
Revises: 
Create Date: 2025-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON

# revision identifiers, used by Alembic.
revision = '001_add_processing_results'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create processing_results table."""
    # Create processing_results table
    op.create_table(
        'processing_results',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('document_id', UUID(as_uuid=True), nullable=False),
        sa.Column('stage', sa.String(100), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('result_data', JSON, nullable=True),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('processing_time_seconds', sa.Float, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.Index('ix_processing_results_document_id', 'document_id'),
        sa.Index('ix_processing_results_stage', 'stage'),
        sa.Index('ix_processing_results_status', 'status'),
        sa.Index('ix_processing_results_created_at', 'created_at'),
    )


def downgrade() -> None:
    """Drop processing_results table."""
    op.drop_table('processing_results')
