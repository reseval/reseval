import random
from string import ascii_lowercase, digits


def string(length, characters=ascii_lowercase + digits):
    """Generate a random string"""
    return ''.join(
        random.SystemRandom().choice(characters) for _ in range(length))
