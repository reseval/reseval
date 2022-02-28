import random
from string import ascii_uppercase, digits


def string(length, characters=ascii_uppercase + digits):
    """Generate a random string"""
    return ''.join(
        random.SystemRandom().choice(characters) for _ in range(length))
