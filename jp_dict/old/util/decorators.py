from logger import logger
from .utils import get_method_name_through_wrapper
from functools import wraps

import sys
import traceback

def assert_test_classmethod(method):
    @wraps(method)
    def assert_test_method_wrapper(self, *args, **kwargs):
        method_name = get_method_name_through_wrapper()
        try:
            method(self, *args, **kwargs)
            logger.good(f"{method_name}: Pass")
        except AssertionError:
            etype, evalue, tb = sys.exc_info()
            e = traceback.format_tb(tb=tb)[-1]
            logger.warning(f"{method_name}: Fail")
            logger.warning(f"{e}")
    return assert_test_method_wrapper