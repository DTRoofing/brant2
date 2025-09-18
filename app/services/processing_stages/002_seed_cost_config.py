"""Seed cost configurations table from JSON file

Revision ID: 2b1a8f9c3d0e
Revises: 001_add_processing_results
Create Date: 2025-09-15 14:30:00.123456

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON
import json
from pathlib import Path
import uuid

# revision identifiers, used by Alembic.
revision = '2b1a8f9c3d0e'
down_revision = '001_add_processing_results' # Replace with the actual revision ID of your previous migration
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Reads the cost_config.json file and inserts it into the cost_configurations table.
    """
    # Define the table structure for the bulk insert operation
    cost_configurations_table = sa.table(
        'cost_configurations',
        sa.column('id', UUID),
        sa.column('key', sa.String),
        sa.column('config_data', JSON)
    )

    # Construct the path to the JSON file relative to this script's location
    # This makes the path relative to the project root where alembic.ini is located.
    project_root = Path(op.get_context().config.config_file_name).parent
    config_path = project_root / "app" / "config" / "cost_config.json"

    if not config_path.exists():
        raise FileNotFoundError(f"Could not find cost_config.json at expected path: {config_path}")

    with open(config_path, 'r') as f:
        config_data = json.load(f)

    # Insert the default configuration data into the table
    op.bulk_insert(cost_configurations_table, [{
        'id': str(uuid.uuid4()),
        'key': 'default',
        'config_data': config_data
    }])

def downgrade() -> None:
    """
    Removes the default cost configuration data from the table.
    """
    op.execute("DELETE FROM cost_configurations WHERE key = 'default'")