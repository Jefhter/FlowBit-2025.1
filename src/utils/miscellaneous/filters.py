
try:
    import regex as re
except ImportError:
    import re

class Filter():
    def set_regex(self, pattern):

        if isinstance(pattern, str):
            self.regex = re.compile(pattern, flags=re.IGNORECASE if self.case_sensitive else 0)

        elif pattern is None:
            self.regex = None

        else:
            self.regex = pattern

    def filter(self, text):

        if self.regex:
            return self.regex.search(text) is not None

        words = text if self.case_sensitive else text.lower()

        if any(word in words for word in self.blacklist):
            return False

        if self.whitelist and not any(word in words for word in self.whitelist):
            return False

        return True







