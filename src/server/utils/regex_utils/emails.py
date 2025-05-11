from .parses import valid_email
import warnings

try:
    import email_validator 
except ImportError:
    warnings.warn(
        "The 'validate_email' module is not installed.\n"
        "Install it using 'pip install validate_email'.\n"
        "Falling back to the built-in 're' module."
    )
    email_validator  = None

try:
    import dns.resolver as dns
except ImportError:
    dns = None

def _check_email(email: str) -> bool:
    if email_validator :
        try:
            valid = email_validator.validate_email(email)
            return True if valid.email else False
        except Exception:
            return False
    else:
        return valid_email(email)

def check_email(email: str, check_dns=False) -> bool:
    """
    Check if the given email is valid.
    Args:
        email (str): The email to check.
        check_dns (bool): Whether to check DNS records for the email domain.)
    Returns:
        bool: True if the email is valid, False otherwise.
    """
    email_sintax = _check_email(email)
    if check_dns and not dns:
        warnings.warn(
            "The 'dnspython' module is not installed.\n"
            "Install it using 'pip install dnspython'.\n"
            "Skipping DNS check."
        )
        check_dns = False

    if check_dns and email_sintax:
        try:
            domain = email.split('@')[1]
            records  = dns.resolver.resolve(domain, 'MX')
            return len(records) > 0
        except Exception:
            return False

    return email_sintax





