import os

from .base import BaseEngine

class SQLite(BaseEngine):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def collation(self):
        return "utf8"

    def parse_url(self, db_path='database.db'):
        return 'sqlite:///{}'.format(os.getenv('DB_PATH', db_path or 'database.db'))