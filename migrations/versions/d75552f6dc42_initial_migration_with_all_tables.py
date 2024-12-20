"""Initial migration with all tables

Revision ID: d75552f6dc42
Revises: 
Create Date: 2024-11-17 09:57:57.092798

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd75552f6dc42'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('books',
    sa.Column('book_id', sa.Integer(), nullable=False),
    sa.Column('api_id', sa.String(length=50), nullable=False),
    sa.Column('title', sa.String(length=100), nullable=False),
    sa.Column('author', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('cover_page', sa.String(length=200), nullable=True),
    sa.PrimaryKeyConstraint('book_id')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=20), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('password', sa.String(length=80), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_table('recommendations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('recommend_book_id', sa.Integer(), nullable=False),
    sa.Column('based_on_book_id', sa.Integer(), nullable=False),
    sa.Column('added_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['based_on_book_id'], ['books.book_id'], ),
    sa.ForeignKeyConstraint(['recommend_book_id'], ['books.book_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('reviews',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('book_id', sa.Integer(), nullable=False),
    sa.Column('rating', sa.Float(), nullable=False),
    sa.Column('review_text', sa.Text(), nullable=True),
    sa.Column('added_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['book_id'], ['books.book_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_read_books',
    sa.Column('record_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('book_id', sa.Integer(), nullable=False),
    sa.Column('read_status', sa.Enum('reading', 'completed', 'to-read', name="('reading', 'completed', 'to-read')"), nullable=False),
    sa.Column('added_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['book_id'], ['books.book_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('record_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_read_books')
    op.drop_table('reviews')
    op.drop_table('recommendations')
    op.drop_table('users')
    op.drop_table('books')
    # ### end Alembic commands ###
