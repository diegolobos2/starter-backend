"""add unique partial index on holds

Revision ID: 0001_add_holds_unique
Revises: 
Create Date: 2026-08-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_add_holds_unique'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Índice parcial: solo considera estados que mantienen la butaca ocupada
    op.create_index(
        'uq_holds_event_seat_active',
        'holds',
        ['event_id', 'seat_id'],
        unique=True,
        postgresql_where=sa.text("status IN ('active','confirmed')"),
        sqlite_where=sa.text("status IN ('active','confirmed')"),
    )


def downgrade():
    op.drop_index('uq_holds_event_seat_active', table_name='holds')
