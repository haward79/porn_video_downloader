
from math import ceil
from pathlib import Path
from sys import stdout
from typing import Dict, List
from urllib.parse import urlparse
import urllib3
from enum import Enum

from library.log_helper import logger


# Disable urllib TLS certificate warning.
urllib3.disable_warnings()


REQUEST_CHUNK_SIZE = 4096
SIZE_NAMES = ('B', 'KB', 'MB', 'GB', 'TB')
REQUEST_HEADER = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0'
}


class BashColor(Enum):
    def __str__(self):
        return self.value

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


def extract_string(string: str, start_index: int, end_delimiter: str) -> str:
    end_index = string.find(end_delimiter, start_index+1)

    if end_index == -1:
        return ''

    return string[start_index:end_index]


def get_unique_filepath(filepath: Path) -> Path:
    original_filepath = filepath
    parent = filepath.parent
    basename = filepath.stem
    extname = filepath.suffix
    no = 1

    while filepath.exists():
        filepath = Path(parent / Path(f'{basename} ({no}){extname}'))
        no += 1

    if original_filepath != filepath:
        logger().info(f'Filepath "{original_filepath}" already exists, so replaced with new filepath "{filepath}".')

    return filepath


def format_url_list(urls: List[str]) -> List[str]:
    urls = urls.copy()

    for i in range(len(urls)):
        if urls[i].endswith('\r\n') or urls[i].endswith('\n\r'):
            urls[i] = urls[i][:-2]
        elif urls[i].endswith('\r') or urls[i].endswith('\n'):
            urls[i] = urls[i][:-1]

    urls = list({url for url in urls if len(url) > 0})

    return urls
