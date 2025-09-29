"""Add Google OAuth fields to users table

Revision ID: 003_add_google_oauth_fields
Revises: 002_seed_cost_config
Create Date: 2025-09-27 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = '003_add_google_oauth_fields'
down_revision = '002_seed_cost_config'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add Google OAuth fields to users table."""
    # Make hashed_password nullable for OAuth users
    op.alter_column('users', 'hashed_password',
                    existing_type=sa.String(255),
                    nullable=True)

    # Add google_id column
    op.add_column('users', sa.Column('google_id', sa.String(255), nullable=True))

    # Add unique constraint and index for google_id
    op.create_unique_constraint('uq_users_google_id', 'users', ['google_id'])
    op.create_index('ix_user_google_id', 'users', ['google_id'])


def downgrade() -> None:
    """Remove Google OAuth fields from users table."""
    # Drop index and unique constraint
    op.drop_index('ix_user_google_id', table_name='users')
    op.drop_constraint('uq_users_google_id', table_name='users', type_='unique')

    # Remove google_id column
    op.drop_column('users', 'google_id')

    # Make hashed_password non-nullable again
    op.alter_column('users', 'hashed_password',
                    existing_type=sa.String(255),
                    nullable=False)

