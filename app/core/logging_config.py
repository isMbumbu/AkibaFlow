import sys
import logging


# Define shared the log format
log_format = '%(levelname)s - %(asctime)s - %(name)s - %(thread)d - %(message)s'


def setup_logging():
    """
    Sets up logging for a Dockerized environment.
    This function is similar to setup_logging but can be customized for Docker-specific needs.

    In a Dockerized environment, you might want to log to stdout/stderr instead of files.
    """

    logging.basicConfig(
        # Set your desired logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)  # Direct logs to stdout
        ]
    )


setup_logging()


# This logger can be used throughout the application
app_logger = logging.getLogger('app_logger')
