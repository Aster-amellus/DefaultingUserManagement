from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_init'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('email', sa.String(length=255), nullable=False, unique=True),
        sa.Column('full_name', sa.String(length=255)),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('TRUE')),
        sa.Column('role', sa.String(length=32), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )

    op.create_table(
        'customers',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False, unique=True),
        sa.Column('industry', sa.String(length=100)),
        sa.Column('region', sa.String(length=100)),
    sa.Column('is_default', sa.Boolean(), nullable=False, server_default=sa.text('FALSE')),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )

    op.create_table(
        'reasons',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('type', sa.String(length=20), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=False),
    sa.Column('enabled', sa.Boolean(), nullable=False, server_default=sa.text('TRUE')),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
    )

    op.create_table(
        'applications',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('type', sa.String(length=20), nullable=False),
        sa.Column('customer_id', sa.Integer(), sa.ForeignKey('customers.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('latest_external_rating', sa.String(length=50)),
        sa.Column('reason_id', sa.Integer(), sa.ForeignKey('reasons.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('severity', sa.String(length=10)),
        sa.Column('remark', sa.Text()),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_by', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL')),
        sa.Column('reviewed_by', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL')),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('reviewed_at', sa.DateTime()),
    )

    op.create_table(
        'application_attachments',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('application_id', sa.Integer(), sa.ForeignKey('applications.id', ondelete='CASCADE'), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('url', sa.String(length=1024), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(), nullable=False),
    )

    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL')),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('target_type', sa.String(length=50), nullable=False),
        sa.Column('target_id', sa.String(length=255)),
        sa.Column('details', sa.Text()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )

    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('content', sa.String(length=512), nullable=False),
    sa.Column('is_read', sa.Boolean(), nullable=False, server_default=sa.text('FALSE')),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )


def downgrade():
    op.drop_table('notifications')
    op.drop_table('audit_logs')
    op.drop_table('application_attachments')
    op.drop_table('applications')
    op.drop_table('reasons')
    op.drop_table('customers')
    op.drop_table('users')
