from datetime import datetime
from typing import List
import warnings

try:
    import regex as re
except ImportError:
    #warnings.warn(
    #    "The 'regex' module is not installed.\n"
    #   "Install it using 'pip install regex'.\n"
    #   "Falling back to the built-in 're' module."
    #)
    import re

VALID_PHONE = re.compile(r'[+()\s-]')
EMAIL_PATTERN = re.compile(
    r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})*$'
)
VALID_USERNAME_RE = re.compile(
    r'^[a-z](?:(?!__)\w){1,30}[a-z\d]$',
    re.IGNORECASE
)

USERNAME_RE = re.compile(
    r'@([a-zA-Z0-9_]+)|(?:https?://)?(?:www\.)?(?:telegram\.(?:me|dog)|t\.me)/([a-zA-Z0-9_]+)'
)
LINK_PATTERN = re.compile(
    r'(https?://|www\.)[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(:\d+)?(/[^\s]*)?',
    re.IGNORECASE
)

DATA_PATTERN = re.compile(
    r'^(0[1-9]|[12]\d|3[01])/(0[1-9]|1[0-2])/\d{4}$'
)

def parse_phone(phone: str|int, min_len: int = 8) -> str|None:
    if isinstance(phone, int):
        return str(phone)
    else:
        phone = VALID_PHONE.sub('', str(phone))
        if phone.isdigit() and len(phone) >= min_len:
            return phone

def parse_nuns(text: str) -> str:
    return re.sub(r'[^0-9]', '', str(text))

def valid_phone(phone: str, min_len: int = 8) -> bool:
    return bool(parse_phone(phone, min_len))

def valid_username(username: str) -> str:
    return bool(VALID_USERNAME_RE.match(username))

def valid_email(email: str) -> bool:
    return bool(EMAIL_PATTERN.match(email))

def valid_link(link: str) -> bool:
    return bool(LINK_PATTERN.match(link))

def search_email(text: str) -> str|None:
    if email := EMAIL_PATTERN.search(text):
        return email.group()

def search_username(text: str) -> str|None:
    if username := USERNAME_RE.search(text):
        return username.group()

def search_phone(text: str) -> str|None:
    if phone := VALID_PHONE.search(text):
        return phone.group()

def search_links(text: str) -> List[str]:
    return LINK_PATTERN.findall(text)

def search_phones(text: str) -> List[str]:
    return VALID_PHONE.findall(text)

def search_emails(text: str) -> List[str]:
    return EMAIL_PATTERN.findall(text)

def search_usernames(text: str) -> List[str]:
    return [match[0] or match[1] for match in USERNAME_RE.findall(text)]

def get_date(data_str: str) -> datetime|None:
    if date := DATA_PATTERN.search(data_str):
        try:
            data_datetime = datetime.strptime(date.group(), "%d/%m/%Y")
            return data_datetime
        except ValueError:
            return None

def get_dates(data_str: str) -> List[datetime]:
    if matchs := DATA_PATTERN.findall(data_str):
        try:
            return [datetime.strptime(date, "%d/%m/%Y") for date in matchs]
        except ValueError:
            return []