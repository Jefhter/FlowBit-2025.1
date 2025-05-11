from abc import ABC, abstractmethod
import sqlite3
import logging
from datetime import datetime, timedelta
from...loggers import getChilder
from ...oop.classes import ResourceWrapper


class DB(ABC):
    def __init__(self, db_path="database.db", conn:sqlite3.Connection=None, base_logger=None, logger_name='sql'):
        if conn:
            self.db_path = None
            self._conn = conn
        else:
            self.db_path = db_path
            self._conn = sqlite3.connect(db_path)
        self.create_tables()

        if not base_logger:
            base_logger = logging.getLogger(logger_name)
            base_logger.setLevel(logging.critical)
        self.logger = getChilder(logger_name, base_logger)

    @property
    def cursor(self) -> sqlite3.Cursor:
        return ResourceWrapper(self.conn.cursor())

    @property
    def conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
        return self._conn

    def __call__(self) -> sqlite3.Cursor:
        return self.conn

    def close(self):
        self.commit()
        self._conn.close()
        self._conn = None

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    @abstractmethod
    def create_tables(self):
        pass

    def execute_query(self, query, data=()):
        with self.cursor as cursor:
            try:
                cursor.execute(query, data)
                self.commit()
                return cursor.fetchall()

            except Exception as e:
                self.logger.error(f"Error executing query: \n{e}")
                self.rollback()
                raise e
            
    def execute_querys(self, query, data=()):
        with self.cursor as cursor:
            try:
                cursor.executemany(query, data)
                self.commit()
                return cursor.fetchall()
            except Exception as e:
                self.logger.error(f"Error executing query: \n{e}")
                self.rollback()
                raise e

    def get_querys(self, query, data=None, to_dict=True):
        with self.cursor as cursor:
            if data:
                cursor.execute(query, data)
            else:
                cursor.execute(query)
            
            if to_dict:
                column_names = [col[0] for col in cursor.description]
                if result := cursor.fetchall():
                    return [
                        dict(zip(column_names, row))
                        for row in result
                    ]
                return result
            return cursor.fetchall()

    def get_query(self, query, data=None, to_dict=True):
        query = query + ' LIMIT 1'
        with self.cursor as cursor:
            if data:    
                cursor.execute(query, data)
            else:
                cursor.execute(query)
            if to_dict:
                column_names = [col[0] for col in cursor.description]
                if result := cursor.fetchone():
                    return dict(zip(column_names, result))
                return {}
            return cursor.fetchone()

    @staticmethod
    def date_to_str(date=None, **delta_kwargs):
        if date is None:
            date = datetime.now()
        if delta_kwargs:
            date += timedelta(**delta_kwargs)
        return date.isoformat()

    @staticmethod
    def str_to_date(date_str=None, **delta_kwargs):
        if date_str is None:
            date = datetime.now()
        else:
            date = datetime.fromisoformat(date_str)
        if delta_kwargs:
            date += timedelta(**delta_kwargs)
        return date

    def convert_data(self, data: str|datetime|None = None, **delta_kwargs):
        if isinstance(data, (datetime, None)):
            return self.date_to_str(data, **delta_kwargs)
        elif isinstance(data, str):
            return self.str_to_date(data, **delta_kwargs)

        raise ValueError("Invalid data type - Should be string or datetime obj")



