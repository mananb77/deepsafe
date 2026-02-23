"""
Password Hashing

Secure password hashing using bcrypt.
"""

import bcrypt

# Number of rounds for bcrypt (2^12 = 4096 iterations)
BCRYPT_ROUNDS = 12


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: Plain text password.

    Returns:
        str: Hashed password.
    """
    salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.

    Args:
        plain_password: Plain text password to verify.
        hashed_password: Hashed password to check against.

    Returns:
        bool: True if password matches, False otherwise.
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


def needs_rehash(hashed_password: str) -> bool:
    """
    Check if a password hash needs to be rehashed.

    This checks if the hash was created with a different number of rounds.

    Args:
        hashed_password: The current password hash.

    Returns:
        bool: True if rehashing is recommended.
    """
    # Extract rounds from hash (format: $2b$XX$...)
    try:
        parts = hashed_password.split("$")
        if len(parts) >= 3:
            current_rounds = int(parts[2])
            return current_rounds != BCRYPT_ROUNDS
    except (ValueError, IndexError):
        pass
    return True  # Rehash if we can't determine rounds
