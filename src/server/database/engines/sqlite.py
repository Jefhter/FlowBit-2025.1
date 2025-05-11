import os
from typing import override

from .base import BaseEngine

class SQLite(BaseEngine):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    @override
    def collation(self):
        return "utf8"

    @override
    def parse_url(self, db_path='database.db'):
        return 'sqlite:///{}'.format(os.getenv('DB_PATH', db_path or 'database.db'))