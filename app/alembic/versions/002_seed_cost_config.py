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
down_revision = '001_add_processing_results'
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
        sa.column('name', sa.String),
        sa.column('description', sa.Text),
        sa.column('base_cost_per_sqft', sa.Float),
        sa.column('material_cost_multiplier', sa.Float),
        sa.column('labor_cost_multiplier', sa.Float),
        sa.column('overhead_multiplier', sa.Float),
        sa.column('regional_multiplier', sa.Float),
        sa.column('is_active', sa.Boolean),
        sa.column('created_at', sa.DateTime),
        sa.column('updated_at', sa.DateTime)
    )

    # Construct the path to the JSON file relative to this script's location
    config_path = Path(__file__).parent.parent.parent / "config" / "cost_config.json"

    if not config_path.exists():
        raise FileNotFoundError(f"Could not find cost_config.json at expected path: {config_path}")

    with open(config_path, 'r') as f:
        config_data = json.load(f)

    # Insert the default configuration data into the table
    op.bulk_insert(cost_configurations_table, [{
        'id': str(uuid.uuid4()),
        'name': 'default',
        'description': 'Default cost configuration from JSON file',
        'base_cost_per_sqft': config_data.get('material_costs_per_sqft', {}).get('asphalt_shingles', 8.0),
        'material_cost_multiplier': 1.0,
        'labor_cost_multiplier': 1.0,
        'overhead_multiplier': config_data.get('overhead_percent', 15.0) / 100.0,
        'regional_multiplier': 1.0,
        'is_active': True,
        'created_at': sa.func.now(),
        'updated_at': sa.func.now()
    }])

def downgrade() -> None:
    """
    Removes the default cost configuration data from the table.
    """
    op.execute("DELETE FROM cost_configurations WHERE name = 'default'")
