from pathlib import Path
from typing import Union, List, Tuple
import sqlite3

from.telethon_utils import parse_phone, clean_phone

def is_sqlite_in_use(db_path: Union[str, Path]) -> bool:
    try:
        conn = sqlite3.connect(str(db_path))
        conn.close()
        return False 
    except (sqlite3.OperationalError, OSError):
        return True  

def get_sessions(
    path:Union[str, Path] ='sessions',
    check_use: bool = True,
) -> List[str]:

    return [
        str(session) 
        for session in Path(path).glob('*.session')
        if not check_use or not is_sqlite_in_use(session)
    ]

def get_sessions_phones(
    path:Union[str, Path] ='sessions',
    replace_paths: bool = False,
) -> List[Tuple[str, Path]]:

    sessions = [Path(session) for session in get_sessions(path, check_use=True)]

    if replace_paths:
        for session in sessions:
            new_name = f'{clean_phone(session.stem)}.session'
            session.with_name(new_name)
            session.rename(new_name)

    return [(parse_phone(session.stem), session) for session in sessions]


