from datetime import datetime
import logging
import pytz

from.consts import DATEFTM, TIMEZONE, normal

class TimeZoneFormatter(logging.Formatter):
    def __init__(
        self, 
        fmt=normal.LEVEL_TIME_MSG, 
        datefmt=DATEFTM, 
        tz=TIMEZONE
    ):
        super().__init__(fmt, datefmt)
        self.tz = pytz.timezone(tz)
        self.datefmt = datefmt

    def formatTime(self, record, datefmt=None) -> str:
        tz = datefmt if datefmt else self.tz
        return self.converter(record.created, tz).strftime(self.datefmt)
    
    def converter(self, timestamp) -> datetime:
        return datetime.fromtimestamp(timestamp).astimezone(self.tz)



