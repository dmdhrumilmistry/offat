import random
import string


def generate_random_string(length):
    """Generate a random string of given length."""
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))
