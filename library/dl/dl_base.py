
from abc import ABC, abstractmethod
from os import environ
from pathlib import Path
from time import sleep
from typing import Type
import curl_cffi
from bs4 import BeautifulSoup
from tqdm import tqdm

from library.ffmpeg_helper import download_m3u8
from library.log_helper import logger
from library.util import REQUEST_CHUNK_SIZE, get_unique_filepath, make_oneline_error_message
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
            title_element.text.strip()
            if title_element is not None
            else
            ''
        )

        for title_suffix in ('XVIDEOS.COM', '五樓自拍', '-'):
            if title.endswith(title_suffix):
                title = title[:-(len(title_suffix))].strip()

        title = title[:max_len]

        logger().debug(f'Fetched website title for "{url}": {title}')

        return title

    @staticmethod
    def handle_request_exception(exception: curl_cffi.exceptions.RequestException) -> None:
        exception_str = str(exception)

        if exception_str.find('Could not resolve host') != -1:
            logger().error(
                'DNS related error occurred. ' +
                'It may due to too many concurrent connection to your DNS server.'
            )
            return

        if exception_str.find('Operation too slow') != -1:
            logger().error(
                'Network speed related error occurred. ' +
                'It may due to poor network connection to Internet or your IP is limited. ' +
                'I will try to sleep 1 minute and retry.'
            )
            sleep(60)

        logger().error(
            'Error occurred during file download. ' +
            f'Here is the error message: {make_oneline_error_message(exception_str)}'
        )

    SELENIUM_FIND_TIMEOUT = 60

    def __init__(self, dl_path: Path, is_silent: bool = False):
        self.__dl_path = dl_path
        self.__is_silent = is_silent
        self.__max_retry = (
            int(dl_max_retry)
            if (
                (dl_max_retry := environ.get('DL_MAX_RETRY')) and
                dl_max_retry.isdigit() and
                int(dl_max_retry) > 0
            )
            else
            5
        )

        if not self.__dl_path.is_dir():
            self.__dl_path.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def _get_video_url(self, url: str, output_title: str) -> Path | None:
        pass

    def _preview_download(self, url: str, referer: str = '') -> str:
        with WebDriver() as web_driver:
            session = web_driver.to_cf_requests(referer)

        try:
            request = session.get(url, stream=True)
        except curl_cffi.exceptions.RequestException as e:
            session.close()
            self.handle_request_exception(e)
            return ''

        if request.status_code != 200:
            request.close()
            session.close()
            return ''

        first_chunk_bytes = next(request.iter_content(chunk_size=REQUEST_CHUNK_SIZE))

        request.close()
        session.close()

        return first_chunk_bytes.decode(errors='ignore')

    def _download_file(self, url: str, filename: Path, referer: str = '', show_progress: bool = False) -> Path | None:
        with WebDriver() as web_driver:
            session = web_driver.to_cf_requests(referer)

        try:
            request = session.get(url, stream=True)
        except curl_cffi.exceptions.RequestException as e:
            session.close()
            self.handle_request_exception(e)
            return None

        if request.status_code != 200:
            request.close()
            session.close()
            logger().error(
                'Error occurred during file download. Here is the error message: ' +
                f'{request.status_code} {make_oneline_error_message(str(request.text))}'
            )
            return None

        content_bytes_str = request.headers.get('content-length')
        content_bytes = None if content_bytes_str is None else int(content_bytes_str)

        if content_bytes is None:
            logger().info('File size reported from server is unavailable')

        filepath = self.dl_path / filename

        with open(filepath, 'wb') as fout:
            # Download file with progress message.
            if show_progress:
                downloaded_bytes = 0

                with tqdm(
                    total=content_bytes,
                    unit='B',
                    unit_scale=True,
                    desc='Download File',
                    disable=(content_bytes is not None)
                ) as progress:
                    try:
                        # Download data for a chunk size at once.
                        for slice_data in request.iter_content(chunk_size=REQUEST_CHUNK_SIZE):
                            # Write chunk to disk.
                            fout.write(slice_data)

                            # Update progress bar.
                            progress.update(len(slice_data))

                            downloaded_bytes += len(slice_data)
                            logger().debug(f'File downloaded {downloaded_bytes} bytes in total {content_bytes} bytes.')

                    except curl_cffi.exceptions.RequestException as e:
                        request.close()
                        session.close()
                        self.handle_request_exception(e)
                        return None

                print()

            # Download file with no message.
            else:
                fout.write(request.content)

        request.close()
        session.close()

        if not filepath.is_file():
            logger().error(f'Downloaded file {filepath} NOT found. This may due to remote sent nothing or no write permission to file.')
            return None

        if content_bytes is None:
            logger().info('Unable to check integrity of downloaded file due to file size is unavailable')
            return filepath

        filesize = filepath.stat().st_size

        if content_bytes != filesize:
            logger().info(f'File "{filepath}" downloaded failed (integrity check NOT passed).')
            filename.unlink(missing_ok=True)
            return None

        logger().info(f'File "{filepath}" downloaded successfully (integrity check passed).')
        return filepath

    def _download_video(self, url: str, output_filename: Path, referer: str = '', level: int = 0) -> Path | None:
        output_filepath = self.dl_path / output_filename
        show_progress = not self.is_silent and level == 0

        downloaded_path = (
            download_m3u8(url, output_filepath, referer, show_progress)
            if self._preview_download(url, referer).startswith("#EXTM3U")
            else
            self._download_file(url, output_filename, referer, show_progress)
        )

        return downloaded_path

    def get_home_url(self) -> str:
        return f'https://{self.get_domain()}/'

    def download(self, url: str, output_title: str = '') -> Path | None:
        if not output_title:
            output_title = self.get_title(url)

        if not output_title:
            logger().error(f'Failed to get video title for the url "{url}".')
            return None

        output_title_escaped = output_title.replace('\\', '').replace('/', '')

        logger().debug('Trying to analysis and download video from the url')
        logger().debug(f'  with url: {url}')
        logger().debug(f'  with download_dir: {self.dl_path}')
        logger().debug(f'  with output_title: {output_title_escaped}')
        logger().debug(f'  with is_silent: {self.is_silent}')
        logger().debug(f'  with max_retry: {self.max_retry}')

        dl_result = None

        for retry_counter in range(self.max_retry):
            logger().debug(f'Try to analysis and download video for {retry_counter + 1} times ...')
            dl_result = self._get_video_url(url, output_title_escaped)
            logger().debug(f'Try to analysis and download video for {retry_counter + 1} times ... Done')

            if dl_result is not None:
                break

        return dl_result

    def download_video(self, url: str, output_filename: str, referer: str = '') -> Path | None:
        if not url or not output_filename:
            return None

        output_filename = get_unique_filepath(self.dl_path / Path(output_filename)).name
        dl_result = None

        for retry_counter in range(self.max_retry):
            logger().debug(f'Try to download video for {retry_counter + 1} times ...')
            dl_result = self._download_video(url, Path(output_filename), referer)
            logger().debug(f'Try to download video for {retry_counter + 1} times ... Done')

            if dl_result is not None:
                break

        return dl_result

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
