"""insert mock user profiles

Revision ID: d706ca5431d5
Revises: 6006e7101ea4
Create Date: 2023-06-25 09:29:39.000160

"""
from alembic import op
import sqlalchemy as sa
import pandas as pd
from uuid import uuid4, UUID


# revision identifiers, used by Alembic.
revision = 'd706ca5431d5'
down_revision = '6006e7101ea4'
branch_labels = None
depends_on = None



def upgrade():
    # get metadata from current connection
    meta = sa.MetaData()
    
    # pass in tuple with tables we want to reflect, otherwise whole database will get reflected
    meta.reflect(bind=op.get_bind(), only=('user',))

    # define table representation
    user_table = sa.Table('user', meta)

    print(f'reflected user table: {user_table}')

    user_data = pd.read_parquet('app/db/migrations/alembic/mock_data/user_profiles.parquet')
    user_data['id'] = user_data['id'].apply(lambda x: UUID(x))
    user_data = user_data.to_dict(orient='records')

    print(f'ready to insert {len(user_data)} user profiles')
    print()
    print(f'first user profile: {user_data[0]}')
    print()
    print(f'last user profile: {user_data[-1]}')
    print()

    user_data = user_data

    for ix, row in enumerate(user_data):
        op.bulk_insert(user_table, [row], multiinsert=False)
        
        if ix % 10000 == 0:
            print(f'inserted {ix} user profiles')

    print('inserted user profiles')
    pass


def downgrade():
    # get metadata from current connection
    meta = sa.MetaData()
    
    # pass in tuple with tables we want to reflect, otherwise whole database will get reflected
    meta.reflect(bind=op.get_bind(), only=('user',))

    # define table representation
    user_table = sa.Table('user', meta)

    print(f'reflected user table: {user_table}')

    op.execute(user_table.delete())
    print('deleted user profiles')

    
