"""Decorators for project."""

import os

from dotenv import load_dotenv


def load_env(func):
    """
    Description
    ----------
    Decorator to load environment variables from a .env file.

    Parameters
    ----------
    :param func: The function to be decorated.

    Returns
    ----------
    :return: The wrapped function that loads environment variables before execution.
    """

    def wrapper(*args, **kwargs):
        if os.path.exists(".env"):
            load_dotenv(".env", override=True)
        return func(*args, **kwargs)

    return wrapper
