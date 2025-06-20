"""初期テーブル作成

Revision ID: 9dfd4987865d
Revises: 
Create Date: 2025-06-20 16:05:43.995958

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9dfd4987865d'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### SQLite対応: テーブル作成のみ ###
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('username', sa.String, unique=True, index=True),
        sa.Column('display_name', sa.String),
        sa.Column('profile_image_url', sa.String),
        sa.Column('is_admin', sa.Boolean, default=False),
        sa.Column('created_at', sa.DateTime),
    )
    op.create_table(
        'posts',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id')),
        sa.Column('post_date', sa.Date, index=True),
        sa.Column('title', sa.String),
        sa.Column('url', sa.String),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime),
        sa.Column('updated_at', sa.DateTime),
    )
    # ### end Alembic commands ###

def downgrade() -> None:
    op.drop_table('posts')
    op.drop_table('users')
