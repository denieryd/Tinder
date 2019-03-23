from functools import wraps
from typing import TypeVar
import re
import time

reg_exp_pattern_access_token = re.compile(
    r'https://oauth\.vk\.com/blank\.html\#access_token=(?P<user_token>\w*)\&\w*=\w*&\w*=\d*')

StrOrInt = TypeVar('StrOrInt', str, int)


class RetryException(BaseException):
    pass


def retry_on_error(arg: int = 5):
    def decor(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            countdown = arg
            while True:
                try:
                    return func(*args, **kwargs)
                except RetryException:
                    print('Please wait. There was an error, we are re-sending your request')
                    if countdown <= 0:
                        break
                    countdown -= 1
                    time.sleep(1)

        return wrapper

    return decor
