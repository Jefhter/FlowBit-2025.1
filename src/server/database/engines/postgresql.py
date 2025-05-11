import os
from typing import override

from sqlalchemy import create_engine

from .base.base import BaseEngine

class PostgreSQL(BaseEngine):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    @override
    def collation(self):
        return 'en_US.UTF-8'
    
    @override
    def parse_url(self, url):
        if not url:
            url = (
                'postgresql+psycopg2://' +
                f"{os.getenv('DB_USER')}:" +  
                f"{os.getenv('DB_PASSWORD')}@" + 
                f"{os.getenv('DB_HOST')}/" + 
                f"{os.getenv('DB_NAME')}"
            )
        return url

