from logging import Logger

from .mariadb import MariaDB
from .sqlite import SQLite
from .postgresql import PostgreSQL
from  .base.base import BaseEngine
from .default import Default
from utils.oop.decorators import singleton

class EngineFactory:
    _engine = None

    @classmethod
    def create_engine(
        cls, 
        engine: str, 
        logger: str | Logger,
        url: str = None, 
        expire_on_commit=False, 
        db_path='database.db', 
        **kwargs
    ) -> BaseEngine:
        if cls._engine:
            return cls._engine 

        if engine == 'mariadb':
            cls._engine = MariaDB(url, expire_on_commit, **kwargs)
        elif engine == 'sqlite':
            cls._engine = SQLite(db_path, expire_on_commit, **kwargs)
        elif engine == 'postgresql':
            cls._engine = PostgreSQL(url, expire_on_commit, **kwargs)
        else:
            cls._engine = Default(url, expire_on_commit, **kwargs)

        cls._engine.logger = logger
        return cls._engine