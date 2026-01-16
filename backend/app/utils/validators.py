import re


def is_valid_4_digit_number(number: str) -> bool:
    """Validate that a string is exactly 4 digits."""
    if not number:
        return False
    return bool(re.match(r"^\d{4}$", number))


def is_valid_player_name(name: str) -> bool:
    """Validate player name (1-50 characters, not empty)."""
    if not name:
        return False
    return 1 <= len(name.strip()) <= 50


def validate_secret_number(number: str) -> tuple[bool, str]:
    """
    Validate secret number and return (is_valid, error_message).
    Returns (True, "") if valid, (False, "error message") if invalid.
    """
    if not number:
        return False, "Secret number is required"
    
    if not number.isdigit():
        return False, "Secret number must contain only digits"
    
    if len(number) != 4:
        return False, "Secret number must be exactly 4 digits"
    
    return True, ""


def validate_guess_number(number: str) -> tuple[bool, str]:
    """
    Validate guess number and return (is_valid, error_message).
    Returns (True, "") if valid, (False, "error message") if invalid.
    """
    if not number:
        return False, "Guess number is required"
    
    if not number.isdigit():
        return False, "Guess must contain only digits"
    
    if len(number) != 4:
        return False, "Guess must be exactly 4 digits"
    
    return True, ""
