import os

from dotenv import load_dotenv
from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base

from functools import wraps 


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
dotenv_path = os.path.join(BASE_DIR, ".env.local")
# print(dotenv_path)
load_dotenv(dotenv_path)

engine = create_engine(os.environ["db_url"], pool_pre_ping=True, pool_size=100, max_overflow=50)
session_factory = sessionmaker(bind=engine, expire_on_commit=False)
Session = scoped_session(session_factory)

metadata = MetaData()

Base = declarative_base()


def close_session(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        res = await func(*args, **kwargs)
        Session.expunge_all()
        Session.remove()
        Session.close()
        return res
    return wrapper

