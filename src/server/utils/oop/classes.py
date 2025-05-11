import threading
from typing import Any
from abc import ABC, abstractclassmethod
from logging import Logger, getLogger, CRITICAL
from ..loggers import getChilder

class Singleton(type):
    __instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls.__instances:
            cls.__instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls.__instances[cls]

class SingletonThread(Singleton):
    __lock = threading.Lock()
    def __call__(cls):
        with cls.__lock:
            return super()(cls)

class WithLogger:
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

        if not base_logger:
            self._logger = getLogger(name)
            self._logger.setLevel(CRITICAL)
            return

        if isinstance(base_logger, str):
            base_logger = getLogger(base_logger)

        self._logger = getChilder(name, base_logger)

class ResourceWrapper:
    def __init__(self, resource: Any, exit_method: str = 'close'):
        self._resource = resource
        self._exit_method = exit_method

    def __getattr__(self, name):
        return getattr(self._resource, name)

    def __enter__(self):
        return self._resource

    def __exit__(self, exc_type, exc_val, exc_tb):
        getattr(self._resource, self._exit_method)()