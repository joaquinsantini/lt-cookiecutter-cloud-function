import logging
import os
import sys
from logging import Logger
from dotenv import load_dotenv


# For Local Test
load_dotenv()


def get_logger() -> Logger:
    """
    Function to retrieve a valid Logger object

    Returns:
        Logger: A valid Logger
    """
    logger = logging.getLogger(
        f"{os.environ.get('K_SERVICE')}.{os.environ.get('FUNCTION_TARGET')}"
    )
    logger.setLevel(logging.DEBUG)

    # Create formatter
    c_handler = logging.StreamHandler()
    c_formatter = logging.Formatter(
        "%(asctime)s - %(funcName)s - %(levelname)s - %(message)s"
    )
    c_handler.setFormatter(c_formatter)

    # Add handlers to the logger
    logger.addHandler(c_handler)

    return logger

def main(request):
    # Get a logger object
    logger = get_logger()
    logger.info("Starting {{cookiecutter.cloud_function_name}}")

    return "Success"


# For Local Test
if __name__ == "__main__":
    main(sys.argv)
