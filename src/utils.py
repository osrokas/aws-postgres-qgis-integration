"""Utility functions for the project."""

import os


def create_random_string(length: int = 10) -> str:
    """
    Description
    ----------
    Generate a random string of specified length.

    Parameters
    ----------
    :param length: Length of the random string to generate.

    Returns
    -------
    :return: Random string of specified length.
    """

    random_string = os.urandom(length).hex()

    return random_string
