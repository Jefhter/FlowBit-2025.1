import re
from typing import Union, Optional
from pathlib import Path
from.. regex_utils.parses import parse_nuns, parse_phone 
USERNAME_RE = re.compile(
    r'@|(?:https?://)?(?:www\.)?(?:telegram\.(?:me|dog)|t\.me)/(@|\+|joinchat/)?'
)
TG_JOIN_RE = re.compile(
    r'tg://(join)\?invite='
)

VALID_USERNAME_RE = re.compile(
    r'^[a-z](?:(?!__)\w){1,30}[a-z\d]$',
    re.IGNORECASE
)


def get_display_name(entity) -> str:
    try:
        first_name = entity.first_name if entity.first_name else ''
        last_name = (' ' + entity.last_name) if  entity.last_name else ''
        return first_name + last_name
    except Exception:
        pass

    try:
        return entity.title
    except Exception:
        pass

    return ''


def clean_phone(phone: Union[str, int, Path]) -> str:
    """
    Removes characters that match the VALID_PHONE pattern and 
    returns only the characters that don't match.

    Args:
        text (str): The string to process.

    Returns:
        str: The filtered string.
    """
    if isinstance(phone, int):
        return str(phone)

    if isinstance(phone, Path):
        phone = phone.stem

    return re.sub(r'[^0-9]', '', str(phone))

def clean_session(session: Union[str, Path]) -> Path:
    """
    Cleans the session string or path to a session file and rename file if existis.

    Args:
        session (Union[str, Path]): The session string or path to the session file.

    Returns:
        Path: The cleaned session string.
    """
    path = Path(session)
    new_path = path.with_name(clean_phone(path.stem) + '.session')

    if str(path) != str(new_path) and path.exists():
        try:
            path.rename(new_path.absolute())
        except:
            return path

    return new_path


def parse_username(username):
    """
    Parses the given username or channel access hash, given
    a string, username or URL. Returns a tuple consisting of
    both the stripped, lowercase username and whether it is
    a joinchat/ hash (in which case is not lowercase'd).

    Returns ``(None, False)`` if the ``username`` or link is not valid.
    """
    username = username.strip()
    m = USERNAME_RE.match(username) or TG_JOIN_RE.match(username)
    if m:
        username = username[m.end():]
        is_invite = bool(m.group(1))
        if is_invite:
            return username, True
        else:
            username = username.rstrip('/')

    if VALID_USERNAME_RE.match(username):
        return username.lower(), False
    else:
        return None, False




