"""create initial schema

Crea las tablas del proyecto. Hasta la Semana 2 el esquema nacía de
`Base.metadata.create_all()` al arrancar la aplicación; desde la Semana 3 el
esquema tiene historia y se construye con migraciones.

Sin esta migración, `alembic upgrade head` sobre una base vacía falla: la
migración del índice supone que la tabla `holds` ya existe.

Revision ID: 0000_create_schema
Revises:
Create Date: 2026-08-02 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0000_create_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'events',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('starts_at', sa.DateTime(), nullable=False),
        sa.Column('ends_at', sa.DateTime(), nullable=False),
    )
    op.create_table(
        'seats',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('event_id', sa.String(), sa.ForeignKey('events.id'), nullable=False),
        sa.Column('label', sa.String(), nullable=False),
    )
    op.create_table(
        'holds',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('event_id', sa.String(), sa.ForeignKey('events.id'), nullable=False),
        sa.Column('seat_id', sa.String(), sa.ForeignKey('seats.id'), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )


def downgrade():
    op.drop_table('holds')
    op.drop_table('seats')
    op.drop_table('events')
