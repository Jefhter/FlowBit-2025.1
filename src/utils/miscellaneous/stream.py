import sys
from.filters import Filter

class StdoutFilter(Filter):
    def __init__(self, std_out = sys.stdout, blacklist=[], whitelist=[], case_sensitive=False, regex=None):
        self.std_out = std_out
        self.case_sensitive = case_sensitive
        self.blacklist = list(blacklist) if not case_sensitive else [word.lower() for word in blacklist]
        self.whitelist = list(whitelist) if not case_sensitive else [word.lower() for word in whitelist]
        self.regex = self.set_regex(regex)
        
    def write(self, text):
        if self.filter(text):
            self.std_out.write(text)

    def flush(self):
        self.std_out.flush()




