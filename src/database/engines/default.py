import os

from .base.base import BaseEngine

class Default(BaseEngine):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def collation(self):
        return 'utf8'
    
    
    def parse_url(self, url):
        if not url:
            url = (
                f"{os.getenv('DB_ENGINE')}://" +
                f"{os.getenv('DB_USER')}:" +  
                f"{os.getenv('DB_PASSWORD')}@" + 
                f"{os.getenv('DB_HOST')}/" + 
                f"{os.getenv('DB_NAME')}"
            )
        return url