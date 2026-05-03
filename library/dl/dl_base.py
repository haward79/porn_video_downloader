
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Type

from library.log_helper import logger


class DlBase(ABC):
    @staticmethod
    def determine_downloader(url: str) -> 'Type[DlBase] | None':
        from library.dl.dl_eight_five import DlEightFive
        from library.dl.dl_five_f import DlFiveF
        from library.dl.dl_xvideos import DlXvideos
        from library.dl.dl_tktube import DlTktube
        from library.dl.dl_iwant import DlIwant

        for downloader in [DlEightFive, DlFiveF, DlXvideos, DlTktube, DlIwant]:
            if url.find(downloader.get_domain()) != -1:
                logger().debug(f'Matched downloader "{downloader.__name__}" for the url "{url}".')
                return downloader

        return None

    @staticmethod
    @abstractmethod
    def get_domain() -> str:
        pass

    def __init__(self, dl_path: Path, is_silent: bool = False):
        self.__dl_path = dl_path
        self.__is_silent = is_silent

    @abstractmethod
    def _download(self, url: str, output_title: str = '') -> Path | None:
        pass

    def get_home_url(self) -> str:
        return f'https://{self.get_domain()}/'

    @abstractmethod
    def get_title(self, url: str) -> str:
        pass

    def download(self, url: str, output_title: str = '') -> Path | None:
        if not output_title:
            output_title = self.get_title(url)

        if not output_title:
            logger().error(f'Failed to get video title for the url "{url}".')
            return None

        output_title_escaped = output_title.replace('\\', '').replace('/', '')

        logger().debug(f'Trying to download video from the url')
        logger().debug(f'  with url: {url}')
        logger().debug(f'  with download_dir: {self.dl_path}')
        logger().debug(f'  with output_title: {output_title_escaped}')
        logger().debug(f'  with is_silent: {self.is_silent}')

        return self._download(url, output_title_escaped)

    @property
    def dl_path(self) -> Path:
        return self.__dl_path

    @property
    def is_silent(self) -> bool:
        return self.__is_silent
