"""Initial tenant schema - Module 1 Task 1.

Revision ID: 0001
Revises: 
Create Date: 2024-06-01 00:00:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create tenants table
    op.create_table(
        'tenants',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('name', sa.String(255), nullable=False, unique=True),
        sa.Column('slug', sa.String(100), nullable=False, unique=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('plan', sa.Enum('starter', 'professional', 'enterprise', name='tenant_plan'), nullable=False, default='starter'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_tenants_slug', 'tenants', ['slug'])

    # Create customers table
    op.create_table(
        'customers',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('domain', sa.String(255), nullable=True),
        sa.Column('contact_email', sa.String(255), nullable=True),
        sa.Column('industry', sa.String(100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_customers_tenant_id', 'customers', ['tenant_id'])

    # Create environments table
    op.create_table(
        'environments',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('customer_id', UUID(as_uuid=True), sa.ForeignKey('customers.id'), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('env_type', sa.Enum('production', 'staging', 'development', 'dr', name='env_type'), nullable=False, default='production'),
        sa.Column('wazuh_manager_url', sa.String(255), nullable=True),
        sa.Column('thehive_url', sa.String(255), nullable=True),
        sa.Column('misp_url', sa.String(255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_environments_customer_id', 'environments', ['customer_id'])


def downgrade() -> None:
    op.drop_table('environments')
    op.drop_table('customers')
    op.drop_table('tenants')
    op.execute('DROP TYPE IF EXISTS tenant_plan')
    op.execute('DROP TYPE IF EXISTS env_type')
