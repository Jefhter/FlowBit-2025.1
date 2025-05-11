from typing import Any
import itertools
from types import GeneratorType
from collections.abc import AsyncIterable
from datetime import datetime, timedelta


__all_ = ['is_list_like', 'convert_iter', 'to_list', 'check_async_iterable', 'chunks']

def is_list_like(obj: Any) -> bool:
    """ Returns `True` if the given object looks like a list-like objects."""
    return isinstance(obj, (list, tuple, set, dict, GeneratorType))

def convert_iter(obj: Any) -> list:
    """ Converts the given object to a list if it is not list-like."""
    return obj if is_list_like(obj) else [obj]

def to_list(obj: Any) -> list:
    """ Converts the given object to a list if it is not list-like, return [] if None"""
    return [_obj for _obj in convert_iter(obj) if _obj is not None]

def check_async_iterable(obj) -> bool:
    return  isinstance(obj, AsyncIterable)

def chunks(iterable, size=100):
    """
    Turns the given iterable into chunks of the specified size,
    which is 100 by default since that's what Telegram uses the most.
    """
    it = iter(iterable)
    size -= 1
    for head in it:
        yield itertools.chain([head], itertools.islice(it, size))

def get_next_time(timezone=None, **target_time):
    currentime = datetime.now(timezone)
    target_time = currentime.replace(**target_time)
    
    if currentime.time() >= target_time.time():
        target_time += timedelta(days=1)
       
    delta = target_time - currentime
    return delta.total_seconds()



