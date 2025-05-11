from sqlalchemy.orm import sessionmaker, Session as BaseSession
from logging import Logger

class Session(BaseSession):
    logger: Logger

class SessionWrapper():
    def __init__(self, session: Session, logger: Logger):
        self._session = session
        self._session.logger = logger
    
    def __getattr__(self, name):
        return getattr(self._session, name)

    def __enter__(self)-> Session:
        return self._session

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._session.close()

class SesssionFactory:
    def __init__(self, engine, expire_on_commit=False):
        self._session_maker = sessionmaker(
            bind=engine, 
            expire_on_commit=expire_on_commit
        )

    def getSession(self, logger: Logger,*args,  **kwargs) -> Session:
        return SessionWrapper(self._session_maker(*args, **kwargs), logger)    



