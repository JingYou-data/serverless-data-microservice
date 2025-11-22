"""
String normalization utilities for data cleaning
"""


def normalize_string(value, default='N/A'):
    """
    Basic string normalization: convert to string and strip whitespace

    Args:
        value: Input value (any type)
        default: Default value if input is None or empty

    Returns:
        str: Normalized string
    """
    if value is None:
        return default

    result = str(value).strip()
    return result if result else default


def normalize_email(email, default='no-email@example.com'):
    """
    Normalize email: lowercase, strip whitespace, validate basic format

    Args:
        email: Email string
        default: Default value for invalid emails

    Returns:
        str: Normalized email
    """
    if not email:
        return default

    cleaned = str(email).strip().lower()

    # Basic format validation
    if '@' in cleaned and '.' in cleaned:
        return cleaned

    return default


def normalize_phone(phone, default='N/A'):
    """
    Normalize phone number: extract only digits

    Args:
        phone: Phone string
        default: Default value if no digits found

    Returns:
        str: Digits only or default
    """
    if not phone:
        return default

    digits = extract_digits(str(phone))
    return digits if digits else default


def normalize_name(name, default='N/A'):
    """
    Normalize name: strip whitespace and title case

    Args:
        name: Name string
        default: Default value if empty

    Returns:
        str: Title-cased name
    """
    if not name:
        return default

    result = str(name).strip().title()
    return result if result else default


def normalize_state(state, default='N/A'):
    """
    Normalize state code: uppercase

    Args:
        state: State code string
        default: Default value if empty

    Returns:
        str: Uppercase state code
    """
    if not state:
        return default

    result = str(state).strip().upper()
    return result if result else default


def normalize_zip_code(zip_code, default='N/A'):
    """
    Normalize zip code: keep only digits and hyphens

    Args:
        zip_code: Zip code string
        default: Default value if invalid

    Returns:
        str: Cleaned zip code
    """
    if not zip_code:
        return default

    cleaned = ''.join(c for c in str(zip_code).strip() if c.isdigit() or c == '-')
    return cleaned if cleaned else default


def extract_digits(value):
    """
    Extract only digits from a string

    Args:
        value: Input string

    Returns:
        str: Digits only
    """
    if not value:
        return ''

    return ''.join(c for c in str(value) if c.isdigit())
