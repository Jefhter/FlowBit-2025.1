import logging

from .consts import LOG_LEVELS

def convert_level(level: str|int ) -> int:
    if isinstance(level, str):
        return getattr(logging, level.upper().replace('ING', ''), logging.DEBUG)
        
    return level

def convert_level_str(level: str|int) -> str:
    if isinstance(level, int):
        return LOG_LEVELS.get(level, 'NONSET')
        
    return level



