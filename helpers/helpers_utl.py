import re


def normalize(text):
    """
    Normalize text for consistent comparison:
    - Lowercase
    - Remove all non-alphanumeric characters
    """
    return re.sub(r"[^a-z0-9]", "", text.lower())
