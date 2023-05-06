from loguru import logger


def exception_handler(func):
    def inner_function(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as error:
            logger.error(f"{func.__name__} failed")
            logger.error(error)
    return inner_function
