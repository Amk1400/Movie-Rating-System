"""create movie schema

Revision ID: 619f6075e35b
Revises: 
Create Date: 2025-12-24 11:04:17.885166

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '619f6075e35b'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "directors",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("birth_year", sa.Integer),
        sa.Column("description", sa.Text),
    )

    op.create_table(
        "movies",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("release_year", sa.Integer),
        sa.Column("cast", sa.Text),
        sa.Column(
            "director_id",
            sa.Integer,
            sa.ForeignKey("directors.id", ondelete="SET NULL"),
        ),
        sa.Column("description", sa.Text),
    )

    op.create_table(
        "genres",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("description", sa.Text),
    )

    op.create_table(
        "movie_genres",
        sa.Column(
            "movie_id",
            sa.Integer,
            sa.ForeignKey("movies.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "genre_id",
            sa.Integer,
            sa.ForeignKey("genres.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )

    op.create_table(
        "movie_ratings",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "movie_id",
            sa.Integer,
            sa.ForeignKey("movies.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "score",
            sa.Integer,
            sa.CheckConstraint("score BETWEEN 1 AND 10"),
            nullable=False,
        ),
        sa.Column(
            "rated_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
        ),
    )


def downgrade():
    op.drop_table("movie_ratings")
    op.drop_table("movie_genres")
    op.drop_table("genres")
    op.drop_table("movies")
    op.drop_table("directors")

