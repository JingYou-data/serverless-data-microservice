"""
Retry and backoff utilities
"""

import random


def calculate_backoff(attempt, initial_backoff=1, is_rate_limit=False):
    """
    Calculate exponential backoff time with jitter

    Args:
        attempt: Current attempt number (0-based)
        initial_backoff: Base backoff time in seconds
        is_rate_limit: If True, use longer wait time for rate limits

    Returns:
        float: Wait time in seconds
    """
    # Exponential backoff: 2^attempt
    base_wait = initial_backoff * (2 ** attempt)

    # Rate limits get longer wait time
    if is_rate_limit:
        base_wait *= 2

    # Add jitter (±25% random variation)
    jitter = base_wait * 0.25 * (random.random() * 2 - 1)

    return base_wait + jitter
