
from math import ceil
from sys import stdout
from typing import Dict
from urllib.parse import urlparse
import urllib3
from enum import Enum


# Disable urllib TLS certificate warning.
urllib3.disable_warnings()


SIZE_NAMES = ('B', 'KB', 'MB', 'GB', 'TB')
REQUEST_HEADER = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0'
}


class BashColor(Enum):
    CLEAR = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'


def get_readable_size(byte_size: int) -> str:
    level = 0
    byte_size_float = float(byte_size)

    while byte_size_float > 1024:
        byte_size_float /= 1024
        level += 1

        if level >= len(SIZE_NAMES) - 1:
            break

    byte_size_float = int(ceil(byte_size_float * 100) / 100)

    return str(byte_size_float) + ' ' + SIZE_NAMES[level]


def is_tty() -> bool:
    return stdout.isatty()


def make_oneline_error_message(message: str) -> str:
    return message.replace('\r', '').replace('\n', '\\n')


def make_request_referer(url: str, referer_url: str = '') -> str:
    if len(referer_url) == 0:
        referer_url = urlparse(url).scheme + '://' + urlparse(url).netloc

    return referer_url


def make_request_header(url: str, referer_url: str = '') -> Dict[str, str]:
    return {
        **REQUEST_HEADER,
        **{
            'Referer': make_request_referer(url, referer_url)
        }
    }
