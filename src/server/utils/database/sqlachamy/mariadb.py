import os
from sqlalchemy import create_engine
from .base import BaseEngine, ujson

class MariaDB(BaseEngine):
    def __init__(self, url=None, base_logger=None, expire_on_commit=False, **kwargs):
        self.expire_on_commit = expire_on_commit
        self.logger = base_logger
        self.engine = self.create_engine(url, **kwargs)
        self.session = self.engine
        self.collation = "utf8mb4_unicode_ci"

    def create_engine(self, url, **kwargs):
        if not url:
            url = (
                'mariadb+mariadbconnector://' +
                f"{os.getenv('DB_USER')}:" +  
                f"{os.getenv('DB_PASSWORD')}@" + 
                f"{os.getenv('DB_HOST')}/" + 
                f"{os.getenv('DB_NAME')}"
            )
        return create_engine(
            url, 
            json_deserializer=ujson.loads,
            json_serializer=ujson.dumps,            
            **kwargs
        )



