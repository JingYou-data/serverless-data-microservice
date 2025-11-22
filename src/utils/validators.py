"""
Data validation utilities
"""


def validate_required_fields(record, required_fields):
    """
    Validate that required fields exist and are not empty

    Args:
        record: Dictionary record to validate
        required_fields: List of required field names

    Returns:
        tuple: (is_valid, error_message)
    """
    for field in required_fields:
        if field not in record:
            return False, f"Missing field: {field}"

        value = record[field]
        if value is None or str(value).strip() == '':
            return False, f"Empty field: {field}"

    return True, None


def validate_email_format(email):
    """
    Validate basic email format

    Args:
        email: Email string to validate

    Returns:
        bool: True if valid format
    """
    if not email:
        return False

    email_str = str(email).strip()
    return '@' in email_str and '.' in email_str


def validate_age_range(age, min_age=0, max_age=120):
    """
    Validate age is within acceptable range

    Args:
        age: Age value
        min_age: Minimum valid age
        max_age: Maximum valid age

    Returns:
        tuple: (is_valid, normalized_age)
    """
    try:
        age_int = int(age) if age else 0
        if min_age <= age_int <= max_age:
            return True, age_int
        return False, 0
    except (ValueError, TypeError):
        return False, 0
