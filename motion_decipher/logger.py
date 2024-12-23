from typing import Callable
from time import localtime, strftime


__reset: str = "\x1b[0m"
__blue: str = "\x1b[34m"
__green: str = "\x1b[32m"
__yellow: str = "\x1b[33m"
__red: str = "\x1b[31m"

__info_head: str = '[' + __blue + "INFO" + __reset + "]: "
__success_head: str = '[' + __green + "SUCCESS" + __reset + "]: "
__warning_head: str = '[' + __yellow + "WARNING" + __reset + "]: "
__error_head: str = '[' + __red + "ERROR" + __reset + "]: "

def __internal_log__(header: str, message: str):
    print(f"{strftime('%m/%d/%Y %H:%M:%S', localtime())} {header}{message}")

log_info: Callable[[str], None] = lambda message : __internal_log__(__info_head, message)
log_success: Callable[[str], None] = lambda message : __internal_log__(__success_head, message)
log_warning: Callable[[str], None] = lambda message : __internal_log__(__warning_head, message)
log_error: Callable[[str], None] = lambda message : __internal_log__(__error_head, message)