import warnings
from typing import List
from.parses import search_links, search_usernames, search_emails

try:
    from urlextract import URLExtract
except ImportError:
    warnings.warn(
        "The 'urlextract' module is not installed.\n"
        "Install it using 'pip install urlextract'.\n"
        "Using regex to extract URLs."
    )
    URLExtract = None

extractor = URLExtract() if URLExtract else None

def search_urls(text: str, ignore_list: List[str] = []) -> List[str]:
    urls = extractor.find_urls(text) if extractor else search_links(text)
    return [url for url in urls if not any(word in url for word in ignore_list)]

def check_spam(
    text: str, 
    ignore_links: List[str] = [],
    ignore_emails: List[str] = [],
    ignore_usernames: List[str] = [],
    black_list_words: List[str] = []
) -> bool:
    if not text:
        return False

    if usernames := search_usernames(text):
        if [username for username in usernames if not any(word in username for word in ignore_usernames)]:
            return True

    if search_urls(text, ignore_links+[]):
        return True

    if emails := search_emails(text):
        if [email for email in emails if not any(word in email for word in ignore_emails)]:
            return True

    if any(word in text.lower() for word in black_list_words):
        return True

    return False
