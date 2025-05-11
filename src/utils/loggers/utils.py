from logging import Logger, getLogger

from .convert import convert_level

def getChilder(
    name: str, 
    base_logger: str|Logger,
    level: int|str|None = None
) -> Logger:

    if isinstance(base_logger, str):
        base_logger = getLogger(base_logger)
    elif not isinstance(base_logger, Logger):
        raise ValueError("Invalid base_logger type")

    logger = getLogger(name)
    logger.setLevel(convert_level(level) if level else base_logger.level)

    for handle in list(base_logger.handlers):
        logger.addHandler(handle)

    for _filter in list(base_logger.filters):
        logger.addFilter(_filter)

    return logger


