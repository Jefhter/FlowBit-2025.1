import logging

class WordFilter(logging.Filter):
    def __init__(self, level, blacklist):
        self.level = level
        self.blacklist = list(blacklist)

    def filter(self, record):
        message = record.getMessage()
        if record.levelno == self.level:
           return not (any (word in message for word in self.blacklist))
        return True




