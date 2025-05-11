import unicodedata
from pathlib import Path
from..files import read_bin, read, write

try:
    import chardet
except ImportError:
    chardet = None

def normalize_to_ascii(text):
    normalized = unicodedata.normalize('NFKD', text)
    ascii_text = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')
    return ascii_text

def detect_encoding(content: str|Path|bytearray|bytes, min_condifent: float = 0.7) -> str:
    if not chardet:
        raise ImportError('Please install the chardet package to use this function.')

    if isinstance(content, (str, Path)):
        content = read_bin(content)

    result = chardet.detect(content)
    return result['encoding'] if result['confidence'] > min_condifent else ''

def recoding(file_path: str|Path, to_encoding: str = 'utf-8', min_condifent: float = 0.7):
    if encoding := detect_encoding(file_path, min_condifent):
        if data := read(file_path, encoding=encoding):
            write(file_path, data, encoding=to_encoding)

