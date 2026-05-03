
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Type
from bs4 import BeautifulSoup

from library.log_helper import logger
from library.web_driver import WebDriver


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

    @staticmethod
    def get_title(url: str, max_len: int = 200) -> str:
        logger().debug(f'Fetching website title for "{url}"')

        with WebDriver() as web_driver:
            web_driver.driver.get(url)
            source_code = web_driver.driver.page_source

        title_element = BeautifulSoup(source_code, "html.parser").find('title')

        title = (
            title_element.text
            if title_element is not None
            else
            ''
        )

        title = title.strip()[:max_len]

        logger().debug(f'Fetched website title for "{url}": {title}')

        return title

    def __init__(self, dl_path: Path, is_silent: bool = False):
        self.__dl_path = dl_path
        self.__is_silent = is_silent
        self.__max_retry = 5

    @abstractmethod
    def _get_video_url(self, url: str, output_title: str) -> Path | None:
        pass

    def get_home_url(self) -> str:
        return f'https://{self.get_domain()}/'

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
        logger().debug(f'  with max_retry: {self.max_retry}')

        dl_result = None

        for retry_counter in range(self.max_retry):
            logger().debug(f'Try to download video for {retry_counter + 1} time ...')
            dl_result = self._get_video_url(url, output_title_escaped)
            logger().debug(f'Try to download video for {retry_counter + 1} time ... Done')

            if dl_result is not None:
                break

        return dl_result

    def download_video(self, url: str, output_filename) -> Path | None:
        # TODO
        pass

    def set_max_retry(self, max_retry: int) -> None:
        if max_retry <= 0:
            return

        self.__max_retry = max_retry

    @property
    def dl_path(self) -> Path:
        return self.__dl_path

    @property
    def is_silent(self) -> bool:
        return self.__is_silent

    @property
    def max_retry(self) -> int:
        return self.__max_retry
