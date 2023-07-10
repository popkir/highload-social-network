import os

from dotenv import load_dotenv
from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base

from random import choice

from functools import wraps 


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
dotenv_path = os.path.join(BASE_DIR, ".env.local")
# print(dotenv_path)
load_dotenv(dotenv_path)


### Modify this part when changing replication settings
db_0_engine = create_engine(os.environ["db_0_url"], pool_pre_ping=True, pool_size=100, max_overflow=50)
db_1_engine = create_engine(os.environ["db_1_url"], pool_pre_ping=True, pool_size=100, max_overflow=50)
db_2_engine = create_engine(os.environ["db_2_url"], pool_pre_ping=True, pool_size=100, max_overflow=50)

master_engine = db_0_engine
slave_engines = [db_1_engine, db_2_engine]

master_session_factory = sessionmaker(bind=master_engine, expire_on_commit=False)
slave_session_factories = [sessionmaker(bind=slave_engine, expire_on_commit=False) for slave_engine in slave_engines]
###

Session = scoped_session(master_session_factory)

class SessionManager:
    master_session = scoped_session(master_session_factory)
    slave_sessions = [scoped_session(s) for s in slave_session_factories]
    current = master_session

metadata = MetaData()
Base = declarative_base()

def close_session(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        res = await func(*args, **kwargs)
        SessionManager.current.expunge_all()
        SessionManager.current.remove()
        SessionManager.current.close()
        return res
    return wrapper

def with_slave(which_slave=None):
    # print('in slave decorator factory')
    # print(SessionManager.current.bind)
    def decorator(func):
        # print('in slave decorator')
        # print(SessionManager.current.bind)
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # print('in wrapper function - substituing session from master to slave')
            # print(SessionManager.current.bind)
            if which_slave is not None:
                SessionManager.current = SessionManager.slave_sessions[which_slave]
            else:
                SessionManager.current = choice(SessionManager.slave_sessions)
            # print(SessionManager.current.bind)
            # print('in wrapper function - launching function')
            res = await func(*args, **kwargs)
            # print('in wrapper function - function finished, substituing session from slave to master')
            SessionManager.current = SessionManager.master_session
            # print(SessionManager.current.bind)
            return res
        return wrapper
    return decorator