from abc import ABC, abstractmethod
from logging import getLogger, CRITICAL, Logger

from sqlalchemy import create_engine

from utils.loggers import getChilder
from .factories import SessionWrapper, Session, SesssionFactory

try:
    import ujson
except ImportError:
    import json as ujson

class BaseEngine(ABC):

    def __init__(self, url=None, expire_on_commit=False, **kwargs):
        self.expire_on_commit = expire_on_commit
        self.engine = self.create_engine(self.parse_url(url), **kwargs)
        
    @abstractmethod
    def parse_url(self, url) -> str:
        pass

    @property
    @abstractmethod
    def collation(self):
        pass

    def create_engine(self, url, **kwargs):
        return create_engine(
            url, 
            json_deserializer=self.json_deserializer,
            json_serializer=self.json_serializer, 
            pool_size=30,         
            max_overflow=20,   
            pool_timeout=60,       
            pool_recycle=3600,
            **kwargs
        )
    
    @property
    def engine(self):
        return self._engine
    
    def close(self):
        self.engine.dispose()

    @engine.setter
    def engine(self, engine):
        self._engine = engine
        self._session_factory = SesssionFactory(engine, self.expire_on_commit)

    @property
    def json_deserializer(self):
        return ujson.loads

    @property
    def json_serializer(self):
        return ujson.dumps

    @property
    def dialect(self):
        return self.engine.dialect

    @property
    def logger(self):
        return self._logger

    @logger.setter
    def logger(self, base_logger: str|Logger):
        if hasattr(self, 'logger_name'):
            name = self.logger_name
        elif hasattr(self, 'name'):
            name = self.name
        elif hasattr(self, '_logger_name'):
            name = self._logger_name
        elif hasattr(self, '_name'):
            name = self._name
        else:
            name = self.__class__.__name__.lower()

        if isinstance(base_logger, str):
            base_logger = getLogger(base_logger)

        if not base_logger:
            self._logger = getLogger(name)
            self._logger.setLevel(CRITICAL)
        else:
            self._logger = getChilder(name, base_logger)

        getLogger('sqlalchemy.engine.Engine').handlers = self._logger.handlers

    @property
    def session(self) -> Session:
        return self()

    def __call__(self) -> Session:
        return self._session_factory.getSession(self.logger)

