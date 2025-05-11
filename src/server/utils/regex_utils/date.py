import warnings
from datetime import datetime
from typing import List
from.parses import get_date, get_dates

__all__ = ["parse_date", "search_date", "search_dates", "get_dates", "get_date"]
try:
    from dateutil.parser import parse
except ImportError:
    warnings.warn(
        "The 'dateutil' module is not installed.\n"
        "Install it using 'pip install python-dateutil'.\n"
        "Falling back to the built-in 're' module."
    )
    parse = None

parse_date = parse

def search_date(
    text: str, 
    dayfirst=True, 
    ignoretz=True, 
    fuzzy=False, 
    raise_exceptions=False
) -> datetime|None:

    if date := get_date(text):
        return date
    elif not parse:
        return None
    try:
        return parse(text, dayfirst=dayfirst, ignoretz=ignoretz, fuzzy=fuzzy)

    except Exception as e:
        if raise_exceptions:
            raise e
        return None

def search_dates(
    text: str, 
    dayfirst=True, 
    ignoretz=True, 
    fuzzy=False, 
) -> List[datetime]:

    dates = []
    sample = ''

    for word in text.split():
        sample += word + ' '
        try:
            if date := parse(sample, dayfirst=dayfirst, ignoretz=ignoretz, fuzzy=fuzzy):
                dates.append(date)
                sample = ''
        except:
            pass

    return dates
