from abc import ABC, abstractmethod
from sqlalchemy.orm import sessionmaker, Session, object_session
from ...oop.classes import ResourceWrapper, WithLogger
from sqlalchemy.ext.declarative import as_declarative

try:
    import ujson
except ImportError:
    import json as ujson

class BaseEngine(ABC, WithLogger):

    @abstractmethod
    def create_engine(self):
        pass

    @property
    def engine(self):
        return self._engine

    @engine.setter
    def engine(self, engine):
        self._engine = self.create_engine(engine) if isinstance(engine, str) else engine

    @property
    def collation(self) -> str:
        return self._collation

    @collation.setter
    def collation(self, collation):
        self._collation = collation

    @property
    def dialect(self):
        return self.engine.dialect

    @property
    def session(self) -> Session:
        return self()

    def __call__(self, *args, **kwargs) -> Session:
        return ResourceWrapper(self._session(*args, **kwargs))

    @session.setter
    def session(self, engine):
        self._session = sessionmaker(
            bind=engine if engine else self.engine,
            expire_on_commit=self.expire_on_commit
      )

@as_declarative()
class Base:
        
    def to_dict(self):
        return {
            key: getattr(self, key)
            for key in self.__mapper__.c.keys()
        }

    def to_json(self, indent=4):
        return ujson.dumps(self.to_dict(), indent=indent, default=str)

    def refresh_obj(self, obj):
        if session := self.session:
            if session.is_active:
                return session.merge(obj)
        return obj

    def __str__(self):
        return self.to_json(2).replace('\"', '')