# import the logging library
import logging
import json

# Get an instance of a logger
logger = logging.getLogger('findings_platform.custom')


def log_info(message):
    logger.info(message)
