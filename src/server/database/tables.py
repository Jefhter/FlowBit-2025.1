import os

from .engines import EngineFactory
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

from logger import LoggerFactory

Base = declarative_base()
engine = EngineFactory().create_engine(
    os.getenv("DB_ENGINE", "sqlite"),
    LoggerFactory().getLogger("database")
)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    username = Column(String(50), unique=True)
    email = Column(String(50), unique=True)
    phone = Column(String(20), unique=True)
    password = Column(String)
    created_at = Column(DateTime, server_default=func.now())

    @property
    def name(self) -> str:
        return f"{self.first_name} {self.last_name or ''}".strip()
    

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    title = Column(String(50), nullable=False)
    description = Column(String(1024))
    status = Column(String(50), server_default="pending")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), server_onupdate=func.now())
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    days = Column(JSON, nullable=False)
    done = Column(Boolean, server_default="0")
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    user = relationship("User", backref="tasks")

Base.metadata.create_all(bind=engine.engine)