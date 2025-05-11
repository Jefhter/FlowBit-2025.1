import sys
import os
import logging
from logging.handlers import BaseRotatingHandler, TimedRotatingFileHandler, RotatingFileHandler
from logging import FileHandler, StreamHandler
from pathlib import Path
from typing import Union, Optional, Dict

import colorlog
from colorlog import ColoredFormatter

from ..miscellaneous.os_utils import os_is_linux
from.consts import colorful, normal, COLOUR_LOG_PATTERN, DATEFTM, DATE_ROTATIVE
from.convert import convert_level

try:
    from concurrent_log_handler import ConcurrentTimedRotatingFileHandler
    from concurrent_log_handler import ConcurrentRotatingFileHandler
except ImportError:
    ConcurrentTimedRotatingFileHandler = TimedRotatingFileHandler
    ConcurrentRotatingFileHandler = RotatingFileHandler


def create_dir(path: Union[str, Path], unix_logs: bool = True) -> str:
    path_file = Path(path) if isinstance(path, str) else path
    
    if unix_logs and os_is_linux():
        app_name = os.getenv('APP_NAME')
        if not app_name:
            app_name = Path(sys.argv[0]).resolve().parent.name

        path_file = Path("/var/log") / app_name / path_file
    
    path_file.parent.mkdir(parents=True, exist_ok=True)
    
    return str(path_file.absolute())


def getColourStreamHandler(
    fmt: str = colorful.LEVEL_TIME_MSG, 
    level: Union[int, str] = logging.INFO,
    datefmt: str = DATEFTM,
    reset: bool = True,
    log_colors: dict = COLOUR_LOG_PATTERN,
    **keyargs
) -> StreamHandler:

    handler = colorlog.StreamHandler()
    handler.setLevel(convert_level(level))
    formater = ColoredFormatter(fmt, datefmt, reset=reset, log_colors=log_colors, **keyargs)
    handler.setFormatter(formater)
    return handler

def getStreamHandler(
    fmt: str = normal.LEVEL_TIME_MSG, 
    level: Union[int, str] = logging.INFO,
    datefmt: str = DATEFTM,
    **keyargs
) -> StreamHandler:

    handler = StreamHandler()
    handler.setLevel(convert_level(level))
    formater = logging.Formatter(fmt, datefmt, **keyargs)
    handler.setFormatter(formater)
    return handler

def getFileHandler(
    file: Union[Path, str] = 'logs.log', 
    level: Union[int, str] = logging.INFO,
    fmt: str = normal.NAME_LEVEL_TIME_MSG,
    datefmt: str = DATEFTM,
    mode: str ='a',
    **keyargs
    ) -> FileHandler: 

    handler = FileHandler(file, encoding='utf-8', mode=mode, **keyargs)
    handler.setLevel(convert_level(level))
    formater = logging.Formatter(fmt, datefmt)
    handler.setFormatter(formater)
    return handler


def getTimedRotativeHandler(
    file: Union[Path, str], 
    level: Union[int, str] = logging.INFO,
    multiprocess: bool = False,
    when: str ='midnight', 
    backupCount: int = 14,
    fmt: str = normal.NAME_LEVEL_TIME_MSG,
    datefmt: str = DATE_ROTATIVE,
    **keyargs
    ) -> BaseRotatingHandler:

    Handler = ConcurrentTimedRotatingFileHandler if multiprocess else TimedRotatingFileHandler

    handler = Handler(
        create_dir(file), 
        when=when, 
        backupCount=backupCount, 
        encoding='utf-8', 
        **keyargs
    )
    handler.setLevel(convert_level(level))
    formater = logging.Formatter(fmt, datefmt)
    handler.setFormatter(formater)
    return handler


def getColourTimedRotativeHandler(
    file: Union[Path, str], 
    level: Union[int, str] = logging.INFO,
    multiprocess: bool = False,
    when: str ='midnight', 
    backupCount: int = 14,
    fmt: str = colorful.NAME_LEVEL_TIME_MSG,
    datefmt: str = DATE_ROTATIVE,
    reset: bool = True,
    log_colours: dict = COLOUR_LOG_PATTERN,
    **keyargs
    ) -> BaseRotatingHandler:

    Handler = ConcurrentTimedRotatingFileHandler if multiprocess else TimedRotatingFileHandler
    handler = Handler(
        create_dir(file), 
        when=when, 
        backupCount=backupCount, 
        encoding='utf-8', 
        **keyargs
    )
    handler.setLevel(convert_level(level))
    formater = ColoredFormatter(fmt, datefmt, reset=reset, log_colors=log_colours)
    handler.setFormatter(formater)
    return handler

def getRotativeHandler(
    file: Union[Path, str], 
    level: Union[int, str] = logging.INFO,
    multiprocess: bool = False,
    maxBytes: int = 1024 * 1024 * 1024, 
    backupCount: int = 14,
    fmt: str = normal.NAME_LEVEL_TIME_MSG,
    datefmt: str = DATEFTM,
    **keyargs
    ) -> BaseRotatingHandler:

    Handler = ConcurrentRotatingFileHandler if multiprocess else RotatingFileHandler

    handler = Handler(
        create_dir(file), 
        maxBytes=maxBytes, 
        backupCount=backupCount, 
        encoding='utf-8', 
        **keyargs
    )
    handler.setLevel(convert_level(level))
    formater = logging.Formatter(fmt, datefmt)
    handler.setFormatter(formater)
    return handler

