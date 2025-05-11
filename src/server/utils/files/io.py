from typing import Union, List, Optional, Tuple
from collections.abc import Iterable
from pathlib import Path
import csv

from..miscellaneous import is_list_like, convert_iter

def read(
    path: Union[str, Path],
    split: bool = False,
    drop_empty: bool = True,
    binary: bool = False,
    encoding: str = 'utf-8',
    ignore_errors: bool = False,
    **kwargs
) -> Union[str, bytes, List[str]]:
    """
    Reads content from a file.

    Args:
        path (Union[str, Path]): The file path to read from.
        encoding (str, optional): Encoding to use for reading text files. Defaults to 'utf-8'.
        split (bool, optional): If True, splits the file content into a list of lines. Defaults to False.
        ignore_errors (bool, optional): If True, returns an empty string or list when an error occurs. Defaults to True.
        binary (bool, optional): If True, reads the file in binary mode. Defaults to False.
        **kwargs: Additional arguments passed to the `open` function.

    Returns:
        Union[str, bytes, List[str]]: The file content as a string, bytes, or list of lines depending on the parameters.

    Raises:
        Exception: Raises an exception if `ignore_errors` is set to False and an error occurs.
    """
    try:

        if binary:
            return read_bin(path, **kwargs)

        text = _read_text(path, encoding, **kwargs)

        if not split:
            return text
        text = text.splitlines()

        if drop_empty:
            return [line.strip() for line in text if line.strip()]
        return text.splitlines()

    except Exception as e:
        if ignore_errors and not binary:
            return '' if split else []
        raise e

def readlines(
    path: Union[str, Path],
    drop_empty: bool = True,
    encoding: str = 'utf-8',
    ignore_errors: bool = False,
    **kwargs
) -> List[str]:
    return readlines(path, split=True, drop_empty=drop_empty, encoding=encoding, ignore_errors=ignore_errors, **kwargs)

def write(
    path: Union[str, Path],
    content: Union[str, bytes, Iterable[str]],
    encoding: str = 'utf-8',
    mode: str = 'w',
    ignore_errors: bool = False,
    binary: bool = False,
    **kwargs
) -> Union[Path, None]:
    """
    Writes content to a file.

    Args:
        path (Union[str, Path]): The file path to write to.
        content (Union[str, bytes, Iterable[str]]): The content to write to the file (text or binary).
        encoding (str, optional): Encoding to use for writing text files. Defaults to 'utf-8'.
        ignore_errors (bool, optional): If True, ignores errors during writing. Defaults to False.
        binary (bool, optional): If True, writes the file in binary mode. Defaults to False.
        **kwargs: Additional arguments passed to the `open` function.

    Returns:
        None

    Raises:
        Exception: Raises an exception if `ignore_errors` is set to False and an error occurs.
    """
    try:
        if binary:
            write_bin(path, content, **kwargs)
        else:
           _write_text(path, encoding, mode, content, **kwargs)

        return Path(path)

    except Exception as e:
        if not ignore_errors:
            raise e


def read_csv(
    path: Union[str, Path],
    delimiter: str = ',',
    encoding: str = 'utf-8',
    ignore_errors: bool = False,
    newline: str ='',
    drop: bool = False,
    skip_header: bool = False,
    **kwargs
) -> List[Optional[Union[List[str], Tuple[str]]]]:
    """
    Reads a CSV file and returns the rows.

    Args:
        path (Union[str, Path]): The file path to the CSV file.
        delimiter (str, optional): The character used to separate fields. Defaults to ','.
        encoding (str, optional): Encoding to use for reading the CSV file. Defaults to 'utf-8'.
        ignore_errors (bool, optional): If True, ignores errors during reading. Defaults to False.
        newline (str, optional): Specifies how newline characters should be handled. Defaults to ''.
        drop (bool, optional): If True, strips whitespace from each field. Defaults to False.
        skip_header (bool, optional): If True, skips the header row of the CSV file. Defaults to False.
        **kwargs: Additional arguments passed to the `csv.reader` function.

    Returns:
        List[Optional[Union[List[str], Tuple[str]]]]: A list of rows, where each row is a list or tuple of strings.

    Raises:
        Exception: Raises an exception if `ignore_errors` is set to False and an error occurs.
    """
    try:
        rows = _read_csv(path, newline, encoding, delimiter, **kwargs)

        if skip_header:
            rows.pop(0)

        if drop:
            rows = set(tuple(map(lambda c: c.strip(), row)) for row in rows)

        return list(rows)

    except Exception as e:
        if not ignore_errors:
            raise e
        return []

def write_csv(
    path: Union[str, Path],
    rows: Iterable[Union[Iterable[str], str]],
    mode: str = 'w',
    delimiter: str = ',',
    encoding: str = 'utf-8',
    newline: str ='',
    header: Optional[Iterable[str]] = None,
    **kwargs
) -> Union[Path, None]:
    """
    Writes data to a CSV file.

    Args:
        path (Union[str, Path]): The file path to write to.
        data (Iterable[Iterable[str]]): Data to write, where each item is a row of strings.
        delimiter (str, optional): The character used to separate fields. Defaults to ','.
        encoding (str, optional): Encoding to use for writing the CSV file. Defaults to 'utf-8'.
        newline (str, optional): Specifies how newline characters should be handled. Defaults to ''.
        header (Optional[Iterable[str]], optional): A list of column headers to write before the data. Defaults to None.
        **kwargs: Additional arguments passed to the `csv.writer` function.

    Returns:
        None
    """
    with open(path, mode=mode, encoding=encoding, newline=newline, **kwargs) as f:
        writer = csv.writer(f, delimiter=delimiter)
        if header:
            writer.writerow(header)
        writer.writerows(convert_iter(rows))
        return Path(path)

def read_bin(path,  **kwargs) -> bytes:
    with open(path, mode='rb', **kwargs) as f:
        return f.read()
    
def write_bin(path, content: bytes, **kwargs) -> None:
    with open(path, mode='wb', **kwargs) as f:
        return f.write(content)
 
def _write_text(path, encoding, mode, content: str|Iterable[str], **kwargs) -> None:
    with open(path, mode, encoding=encoding, **kwargs) as f:
        if is_list_like(content):
            f.writelines(content)
        else:
            f.write(content)

def _read_text(path, encoding, **kwargs) -> Union[str, List[str]]:
    with open(path, encoding=encoding, **kwargs) as f:
        return f.read()

def _read_csv(path, newline, encoding, delimiter, **kwargs) -> List[List[str]]:
    with open(path, newline=newline, encoding=encoding, **kwargs) as f:
        return list(csv.reader(f, delimiter=delimiter))



