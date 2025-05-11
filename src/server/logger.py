import logging
import os

from utils.loggers.handles import getColourStreamHandler, getTimedRotativeHandler, colorful
from utils.loggers import getChilder
from utils.loggers.convert import convert_level

__all__ = ['LoggerFactory']

LOG_LEVEL = convert_level(os.getenv('LOG_LEVEL', 'DEBUG'))
DB_LOG_LEVEL = convert_level(os.getenv('DB_LOG_LEVEL', 'ERROR'))
LOG_FILE = os.getenv('LOG_FILE', 'false').lower() == 'true'

class ServerLogger:    
    @staticmethod
    def getLogger(level) -> logging.Logger:
        logger = logging.getLogger('server')
        logger.setLevel(level)

        stream_logger = getColourStreamHandler(fmt=colorful.NAME_LEVEL_TIME_MSG, level=level)
        logger.addHandler(stream_logger)

        if LOG_FILE:
            timed_logger = getTimedRotativeHandler('logs/server.log', 'DEBUG')
            logger.addHandler(timed_logger)

        return logger

class DBLogger:
    @staticmethod
    def getLogger(level) -> logging.Logger:
        logger = logging.getLogger('database')
        logger.setLevel(level)
        stream_logger = getColourStreamHandler(fmt=colorful.NAME_LEVEL_TIME_MSG, level=level)
        logger.addHandler(stream_logger)
        return logger
    
class LoggerFactory:
    _instances = {}

    @classmethod
    def getLogger(cls, name: str) -> logging.Logger:
        if name in cls._instances:
            return cls._instances[name]
        
        if name == 'server':
            logger = ServerLogger.getLogger(LOG_LEVEL)
        elif name == 'database':
            logger = DBLogger.getLogger(DB_LOG_LEVEL)
        else:
            logger = getChilder(name, cls._instances['server'], LOG_LEVEL)

        cls._instances[name] = logger
        return logger

