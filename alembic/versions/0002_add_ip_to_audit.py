from alembic import op
import sqlalchemy as sa

revision = '0002_add_ip_to_audit'
down_revision = '0001_init'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('audit_logs', sa.Column('ip', sa.String(length=64), nullable=True))


def downgrade():
    op.drop_column('audit_logs', 'ip')
