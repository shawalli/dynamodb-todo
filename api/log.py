import logging


def get_logger(log_name=None):
    if len(logging.getLogger(name=log_name).handlers) > 0:
        logger = logging.getLogger(name=log_name)
        logger.setLevel(logging.INFO)
    else:
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(name=log_name)

    return logger