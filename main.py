
# Import library.
from typing import List, Dict
import logging
import argparse
from pathlib import Path
from os import chdir
from math import ceil
from time import sleep
from sys import stdout
import json
from tqdm import tqdm
from bs4 import BeautifulSoup
from ffmpeg import FFmpeg
from ffmpeg.errors import FFmpegError
import urllib
import urllib3
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, InvalidArgumentException, WebDriverException, TimeoutException

# Disable urllib TLS certificate warning.
urllib3.disable_warnings()


# Define constant.
URL_FAILED_FILENAME = 'url_failed.txt'
SIZE_NAMES = ('B', 'KB', 'MB', 'GB', 'TB')
REQUEST_HEADER = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0'}
REQUEST_CHUNK_SIZE = 4096
MAX_FILENAME_LENGTH = 90


# Define class.
class BashColor:
    # Constants.
    CLEAR = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'


def self_test_data() -> List[Dict[str,str|int|None]]:
    return [
        {
            'url': 'https://www.85po.com/v/11978/gao-zhong-mei-tuo-yi-zi-pai-36/',
            'filepath': None,
            'duration': None,
            'size': None
        },
        {
            'url': 'https://www.porn5f.com/video/127685/%E5%90%83%E8%82%89%E6%A3%92',
            'filepath': 'download/吃肉棒 - 五樓自拍.ts',
            'duration': None,
            'size': 53914264
        },
        {
            'url': 'https://www.xvideos.com/video.hmcoeofdd90/_',
            'filepath': 'download/[無碼]女王大人幫我擼到射 - XVIDEOS.COM.ts',
            'duration': None,
            'size': 8825660
        },
        {
            'url': 'https://tktube.com/videos/296295/011925-01/',
            'filepath': 'download/天然むすめ 011925_01 息継ぎするのを忘れるくらい一生懸命！喉奥までぶっこむ連続ご奉仕！細川洋子.mp4',
            'duration': None,
            'size': 8860
        },
        {
            'url': 'https://iwant-sex.com/video/24749.html',
            'filepath': None,
            'duration': None,
            'size': None
        },
    ]


# Define function.
def init_logger(work_dir: str) -> logging.Logger:
    filename = Path(work_dir, 'CHECKME.log')
    logging.basicConfig(filename=filename, level=logging.CRITICAL, format='%(asctime)s|%(levelname)s|%(message)s')

    logger = logging.getLogger('porn_video_downloader')
    logger.setLevel(logging.DEBUG)

    logger.debug('Logging start')

    return logger


def is_tty() -> bool:
    return stdout.isatty()


def get_args_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Download porn videos. '
                                                 'Interactive mode: program will get parameters and input from user input. '
                                                 'Batch mode: program will get parameters and input from arguments. '
                                                 'To use interactive mode, please run with argument urls_path unset. '
                                                 'To use batch mode, please run with argument urls_path set.')
    parser.add_argument('--urls-file', dest='urls_path', help='File path which contains urls to be downloaded')
    parser.add_argument('--download-dir', dest='download_dir', help='Download directory to save downloaded videos')
    parser.add_argument('--work-dir', dest='work_dir', default='./', help='Working directory to output log file')
    parser.add_argument('--is-silent', dest='is_silent', action='store_true', help='Silent download with no extra output')
    parser.add_argument('--self-test', dest='self_test', action='store_true', help='Do self test and this will ignore --urls-file argument')

    return parser


def check_args(args: argparse.Namespace) -> List[str]:
    error_messages = []

    if args.urls_path is not None and not Path(args.urls_path).is_file():
        error_messages.append('--urls-file parameter error: must be a FILE')

    if args.download_dir is not None and not Path(args.download_dir).is_dir():
        error_messages.append('--download-dir parameter error: must be a existed DIRECTORY')

    if args.work_dir is not None and not Path(args.work_dir).is_dir():
        error_messages.append('--work-dir parameter error: must be a existed DIRECTORY')

    return error_messages


def get_readable_size(byte_size: int) -> str:
    level = 0
    byte_size = float(byte_size)

    while byte_size > 1024:
        byte_size /= 1024
        level += 1

        if level >= len(SIZE_NAMES) - 1:
            break

    byte_size = int(ceil(byte_size * 100) / 100)

    return str(byte_size) + ' ' + SIZE_NAMES[level]


def fetch_string(string: str, start_index: int, end_delimiter: str) -> str:
    end_index = string.find(end_delimiter, start_index+1)

    if end_index == -1:
        return ''
    else:
        return string[start_index:end_index]


def format_url_list(urls: List[str]) -> List[str]:
    urls = urls.copy()

    for i in range(len(urls)):
        if urls[i].endswith('\r\n') or urls[i].endswith('\n\r'):
            urls[i] = urls[i][:-2]
        elif urls[i].endswith('\r') or urls[i].endswith('\n'):
            urls[i] = urls[i][:-1]

    urls = list(set([url for url in urls if len(url) > 0]))

    return urls


def extract_url_resolution_xvideos(url: str) -> int:
    resolution = -1
    start_index = url.find('hls-')

    if start_index != -1:
        start_index += 4
        resolution_ = fetch_string(url, start_index, 'p')

        if len(resolution_) > 0:
            resolution = int(resolution_)

    return resolution


def extract_url_resolution_missav(url: str) -> int:
    resolution = -1
    ending_index = url.find('/video.m3u8')

    if ending_index != -1:
        size = url[:ending_index].split('x')

        if len(size) == 2 and size[0].isdigit() and size[1].isdigit():
            resolution = int(size[1])

    return resolution


def get_max_resolution_url(urls: List[str]) -> str:
    logger.debug('Picking max resolution segment.')
    resolutions = []

    for i, url in enumerate(urls):
        resolution_xvideos = extract_url_resolution_xvideos(url)
        resolution_missav = extract_url_resolution_missav(url)

        if resolution_xvideos > 0:
            resolutions.append(resolution_xvideos)
        elif resolution_missav > 0:
            resolutions.append(resolution_missav)

    if len(resolutions) > 0:
        if len(resolutions) == len(list(set(resolutions))):
            resolutions.sort(reverse=True)
            target_resolution = resolutions[0]

            for i, url in enumerate(urls):
                resolution_xvideos = extract_url_resolution_xvideos(url)
                resolution_missav = extract_url_resolution_missav(url)

                if resolution_xvideos > 0 and resolution_xvideos == target_resolution:
                    logger.debug(f'Max resolution is set to url "{url}" for xvideos.')
                    logger.debug('Checking max resolution segment......Done')
                    return url

                elif resolution_missav > 0 and resolution_missav == target_resolution:
                    logger.debug(f'Max resolution is set to url "{url}" for missav.')
                    logger.debug('Checking max resolution segment......Done')
                    return url

            logger.debug('No resolution url found. (Url has existed but missing now.)')
            logger.debug('Checking max resolution segment......Done')
            return ''

        else:
            logger.debug('No resolution url found. (Resolutions are the same.)')
            logger.debug('Checking max resolution segment......Done')
            return ''

    else:
        logger.debug('No resolution url found.')
        logger.debug('Checking max resolution segment......Done')
        return ''


def create_selenium_instance() -> webdriver.firefox.webdriver.WebDriver:
    firefox_options = webdriver.FirefoxOptions()
    # firefox_options.add_argument('-headless')

    firefox = webdriver.Firefox(options=firefox_options)

    return firefox


def clear_selenium_files() -> None:
    logger.debug('Removing geckodriver log file.')

    log = Path('geckodriver.log')

    if log.is_file():
        log.unlink()
        logger.debug('Removed geckodriver log file.')

    logger.debug('Removing geckodriver log file......Done')


def selenium_get_url(firefox: webdriver.firefox.webdriver.WebDriver, url: str, referer_url: str | None = None) -> bool:
    try:
        if referer_url is None or len(referer_url) == 0:
            referer_url = url

        logger.debug(f'Loading referer url "{url}" .')
        firefox.get(referer_url)
        sleep(3)

        logger.debug(f'Loading url "{url}" .')
        firefox.get(url)

    except InvalidArgumentException as e:
        logger.debug(f'Invalid selenium argument with url "{url}" and referer_url "{referer_url}".' + str(e).replace('\n', '\\n').replace('\r', ''))
        return False

    except WebDriverException as e:
        # A DNS error.
        if str(e).find('neterror?e=dnsNotFound') != -1:
            logger.debug('DNS related error occurred. It may due to too many concurrent connection to your DNS server.')
            sleep(3)
            return selenium_get_url(firefox, url, referer_url)

        # NOT a DNS error.
        else:
            logger.debug(f'Error occurred during url loading. Here is the error message.\n{str(e).replace('\n', '\\n').replace('\r', '')}')
            return False

    return True


def selenium_load_url(url: str, preload_times: int = 0, referer_url: str = None) -> webdriver.firefox.webdriver.WebDriver:
    firefox = create_selenium_instance()

    # Preload url.
    if preload_times >= 0:
        logger.debug('Do preload......')

        for i in range(preload_times):
            logger.debug(f'Do preload......{i+1}/{preload_times}')

            if selenium_get_url(firefox, url, referer_url):
                logger.debug(f'Do preload......{i+1}/{preload_times} Success')
            else:
                logger.debug(f'Do preload......{i+1}/{preload_times} Failed')

            sleep(1)

        logger.debug('Do preload......Done')

    else:
        print('Invalid parameter: preload_times should be a integer equal or greater than 0.')
        logger.info('Invalid parameter: preload_times should be a integer equal or greater than 0.')
        firefox.quit()
        return None

    # Formally load url.
    logger.debug(f'Formally load url "{url}" .')

    while not selenium_get_url(firefox, url, referer_url):
        logger.debug(f'Failed to load url "{url}" formally. Keep trying.')
        sleep(3)

    return firefox


def get_website_code(url: str, referer_url: str = None) -> str:
    source_code = ''

    if url.find('85po.com') != -1:
        firefox = selenium_load_url(url, preload_times=5, referer_url=referer_url)
    else:
        firefox = selenium_load_url(url, referer_url=referer_url)

    if firefox is not None:
        source_code = firefox.page_source
        firefox.quit()

        logger.debug(f'Successfully get source code for the url.')
    else:
        logger.debug(f'Failed to get source code for the url due to previous error.')

    return source_code


def get_website_title(url: str, referer_url: str = None) -> str:
    logger.debug(f'Try to get website title from the url "{url}".')

    source_code = get_website_code(url, referer_url)
    bs = BeautifulSoup(source_code, "html.parser")
    website_title_element = bs.find('title')

    if website_title_element is not None:
        website_title = website_title_element.text
    else:
        website_title = ''

    return website_title


def clip_filename(filepath: str) -> str:
    parent = str(Path(filepath).parent) + '/'
    basename = Path(filepath).stem
    extname = Path(filepath).suffix

    pos = basename.find('.part')

    if pos != -1:
        extname = basename[pos:] + extname
        basename = basename[:pos]

    clipped_filepath = parent + basename[:MAX_FILENAME_LENGTH - len(extname)] + extname

    return clipped_filepath


def download_file(url: str, filepath: str, is_silent: bool = False, is_top: bool = True, referer_url: str = None) -> str:
    is_success = False

    if is_top:
        print(f'\nDownloading file "{filepath}".')
    logger.info(f'Downloading file "{filepath}" from "{url}".')

    # Check length of filename with extension name is under the limit.
    original_filepath = filepath
    filepath = clip_filename(filepath)

    if original_filepath != filepath:
        logger.info('Filename exceed MAX_FILENAME_LENGTH. filename is clipped.')
        logger.debug(f'Original filepath is "{original_filepath}".')
        logger.debug(f'Clipped filepath is "{filepath}".')

    # Retry 10 times due to some files are really large!
    for retry_count in range(10):
        if is_top:
            print(f'\nTry to download for {retry_count + 1} time(s).')
        logger.info(f'Try to download for {retry_count + 1} time(s).')

        # Set request header for the next request.
        if referer_url is None:
            request_header = REQUEST_HEADER
        else:
            request_header = {**REQUEST_HEADER, **{'Referer': referer_url}}

        # Open file request to server and get file size.
        try:
            request = requests.get(url, stream=True, headers=request_header, verify=False)

        except requests.exceptions.ConnectionError as e:
            # A DNS error.
            if str(e).find('Temporary failure in name resolution') != -1:
                logger.debug('DNS related error occurred. It may due to too many concurrent connection to your DNS server.')

            # NOT an DNS error.
            else:
                logger.debug(f'Error occurred. Here is the error message.\n{str(e).replace('\n', '\\n').replace('\r', '')}')

            continue

        content_bytes = request.headers.get('content-length')

        # Format file size and output it.
        if content_bytes is None:
            if is_top:
                print('File size reported from server is unavailable.')
        else:
            content_bytes = int(content_bytes)

        logger.debug(f'File size reported from server is {content_bytes} bytes ().')

        # Clear content of download file.
        Path(filepath).unlink(missing_ok=True)

        '''
        Download file.
        '''
        with open(filepath, "ab") as fout:
            # Download file with no message.
            if not is_top or is_silent or content_bytes is None:
                fout.write(request.content)

            # Download file with progress message.
            else:
                downloaded_bytes = 0

                with tqdm(total=content_bytes, unit='B', unit_scale=True, desc='Download File', disable=is_tty()) as progress:
                    # Download data for chunk size at once.
                    for slice_data in request.iter_content(chunk_size=REQUEST_CHUNK_SIZE):
                        # Write chunk to disk.
                        fout.write(slice_data)

                        # Print progress bar.
                        progress.update(len(slice_data))

                        logger.info(f'File downloaded for {downloaded_bytes} bytes in {content_bytes} bytes.')

                print()

        # Release request.
        request.close()

        '''
        Check integrity of downloaded file.
        '''
        file = Path(filepath)

        if file.is_file():
            filesize = file.stat().st_size

            if content_bytes is None:
                logger.debug('Unable to check integrity of downloaded file due to file size is unavailable.')
                is_success = True
            else:
                if content_bytes == filesize:
                    logger.debug('File downloaded successfully (integrity check passed).')
                    is_success = True
                else:
                    logger.debug('File downloaded failed (integrity check NOT passed).')

                    file.unlink()
                    logger.debug('Downloaded file is removed from disk.')

        else:
            logger.debug('Downloaded file NOT found. This may due to no write permission to file.')

        if is_success:
            break

    # Check if downloaded file is a playlist.
    if is_success:
        with open(filepath, 'rb') as fin:
            start_bytes = fin.read(7)

        # Download playlist.
        if start_bytes == b'#EXTM3U':
            if is_top and not is_silent:
                print('\nDownloading playlist recursively.')
            logger.info('Downloading playlist recursively.')

            original_url = url

            with open(filepath) as fin:
                lines = fin.readlines()

            urls = [line for line in lines if not line.startswith('#')]
            urls = format_url_list(urls)

            # Check if urls in playlist are different resolution.
            max_resolution_url = get_max_resolution_url(urls)

            logger.info(f'urls: {urls}')
            logger.info(f'max_resolution_url: {max_resolution_url}')

            if len(max_resolution_url) > 0:
                urls = [max_resolution_url,]

            # Fix url without full url in playlist.
            for i, url in enumerate(urls):
                if url.startswith('https://') or url.startswith('http://'):
                    pass
                else:
                    urls[i] = urllib.parse.urljoin(original_url, url)

            # Download all segments.
            filepath_base = filepath
            merge_files = []

            with tqdm(total=len(urls), unit='Segment', unit_scale=False, desc='Download Segments', disable=(is_tty() and is_top and not is_silent)) as progress:
                for i, url in enumerate(urls):
                    logger.debug(f'Downloading segment part {i+1}.')
                    filepath_subfile = download_file(url, filepath_base + '.part' + str(i+1), is_silent, False, referer_url)
                    merge_files.append(filepath_subfile)
                    logger.debug(f'Downloading segment part {i + 1}......Done')
                    logger.debug(f'Segment file is saved to "{filepath_subfile}".')

                    # Print progress bar.
                    progress.update(1)

            if is_tty() and is_top and not is_silent:
                print()

            # Merge segments and remove it from disk.
            with open(filepath, 'wb') as fout:
                logger.debug(f'Merging segment parts to "{filepath}".')
                logger.debug(f'Segment parts are listed: "[{", ".join(merge_files)}]".')

                for merge_file in merge_files:
                    with open(merge_file, 'rb') as fin:
                        content = fin.read(Path(merge_file).stat().st_size)
                    Path(merge_file).unlink()

                    fout.write(content)

                logger.debug(f'Merging segment parts to "{filepath}"......Done')

            if is_top:
                print('Downloading playlist recursively......Done\n')
            logger.info('Downloading playlist recursively......Done')

    if is_top:
        print(f'Downloading file "{filepath}"......Done')
    logger.info(f'Downloading file "{filepath}" from "{url}"......Done')

    if is_success:
        return filepath
    else:
        return ''


def download_video(url: str, download_dir: str | None = None, filename: str | None = None, is_silent: bool = False) -> bool:
    '''
    Setup parameters.
    '''

    logger.debug(f'Trying to download video from the url.')
    logger.debug(f'  with parameter url: {url}')
    logger.debug(f'  with parameter download_dir: {download_dir}')
    logger.debug(f'  with parameter filename: {filename}')
    logger.debug(f'  with parameter is_silent: {is_silent}')

    # Set download directory to current working directory by default.
    if download_dir is None or len(download_dir) == 0:
        download_dir = './'
        logger.debug(f'  with parameter download_dir changed to: {download_dir}')

    # Get filename from website title by default.
    if filename is None or len(filename) == 0:
        filename = get_website_title(url).replace('\\', '_').replace('/', '_')

        if len(filename) == 0:
            print('Failed to get website title as filename.')
            logger.info('Failed to get website title as filename.')

            return False

    # Get filename with no extension.
    else:
        filename = Path(filename).stem

    logger.debug(f'Parameter filename is set to "{filename}".')


    '''
    Download video.
    '''

    # It's from 85po.com .
    if url.find('85po.com') != -1:
        logger.debug('It\'s a url from 85po.')
        video_url = ''

        # Get video url from source code of web page.
        for retry_counter in range(5):
            logger.debug(f'[{retry_counter + 1}] Try to locate video element on web page.')
            firefox = selenium_load_url(url)

            try:
                video = firefox.find_element(By.CSS_SELECTOR, '#kt_player video')
            except NoSuchElementException:
                logger.debug('Failed to locate video element on web page.')
                sleep(1)
            else:
                logger.debug('Successful to locate video element on web page.')
                video_url = video.get_attribute('src')
                firefox.quit()
                break

            firefox.quit()

        # Check if we get the video url.
        if len(video_url) > 0:
            if len(download_file(video_url, str(Path(download_dir, filename + '.mp4')), is_silent)) == 0:
                return False
        else:
            logger.debug('Failed to get video url.')
            return False

    # It's from porn5f.com .
    elif url.find('www.porn5f.com') != -1:
        logger.debug('It\'s a url from porn5f.')
        video_url = ''

        source_code = get_website_code(url)
        bs = BeautifulSoup(source_code, "html.parser")
        video_urls = [element.find('source').attrs.get('src') for element in bs.find_all('video') if element.find('source') is not None]
        video_urls = [url for url in video_urls if url is not None and url.find('porn5f.com') != -1]
        video_url = video_urls[0] if len(video_urls) > 0 and len(video_urls[0]) > 0 else None

        # Check if we get the video url.
        if video_url is not None:
            if len(download_file(video_url, str(Path(download_dir, filename + '.ts')), is_silent)) == 0:
                return False
        else:
            logger.debug('Failed to get video url.')
            return False

    # It's from xvideos.com .
    elif url.find('www.xvideos.com') != -1:
        logger.debug('It\'s a url from xvideos.')
        video_url = ''

        source_code = get_website_code(url)
        pos = source_code.find('html5player.setVideoHLS')

        if pos != -1:
            video_url = fetch_string(source_code, pos + 25, "'")

        # Check if we get the video url.
        if len(video_url) > 0:
            if len(download_file(video_url, str(Path(download_dir, filename + '.ts')), is_silent)) == 0:
                return False
        else:
            logger.debug('Failed to get video url.')
            return False

    # It's from tktube.com .
    elif url.find('tktube.com') != -1:
        logger.debug('It\'s a url from tktube.')
        video_url = ''

        # Fetch video url.
        firefox = selenium_load_url(url)

        try:
            show_video_button = firefox.find_element(By.CSS_SELECTOR, '.fp-ui')
            firefox.execute_script('arguments[0].click();', show_video_button)
            WebDriverWait(firefox, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, "video[src*='/get_file/']")))
            video = firefox.find_element(By.CSS_SELECTOR, "video[src*='/get_file/']")
            video_url = video.get_attribute('src')

        except (NoSuchElementException, TimeoutException) as e:
            logger.debug('Failed to get video url. Exception occurred.')
            logger.debug(e)
            firefox.quit()
            return False

        firefox.quit()

        # Check if we get the video url.
        if len(video_url) > 0:
            if len(download_file(video_url, str(Path(download_dir, filename + '.mp4')), is_silent)) == 0:
                return False
        else:
            logger.debug('Failed to get video url. The url is empty.')
            return False

    # It's from missav.com .
    elif url.find('missav.com') != -1:
        logger.debug('It\'s a url from missav.')
        video_url = ''

        for retry_counter in range(5):
            logger.debug(f'[{retry_counter + 1}] Try to fetch video url from web page.')

            # Fetch video url.
            firefox = selenium_load_url(url)
            sleep(3)
            entries = firefox.execute_script('return window.performance.getEntries();')

            for entry in entries:
                if entry['name'].find('playlist.m3u8') != -1:
                    video_url = entry['name']

            if len(video_url) > 0:
                logger.debug('Successful to fetch video url from web page.')
                firefox.quit()
                break
            else:
                logger.debug('Failed to fetch video url from web page.')
                sleep(5)

            firefox.quit()

        # Check if we get the video url.
        if len(video_url) > 0:
            if len(download_file(video_url, str(Path(download_dir, filename + '.ts')), is_silent, referer_url=url)) == 0:
                return False
        else:
            logger.debug('Failed to get video url. The url is empty.')
            return False

    # It's from iwant-sex.com .
    elif url.find('iwant-sex.com') != -1:
        logger.debug('It\'s a url from iwant-sex.')
        video_url = ''

        for retry_counter in range(5):
            logger.debug(f'[{retry_counter + 1}] Try to fetch video url from web page.')

            # Fetch video url.
            firefox = selenium_load_url(url, 0, url)
            sleep(3)
            entries = firefox.execute_script('return window.performance.getEntries();')

            for entry in entries:
                if entry['name'].find('.m3u8') != -1:
                    video_url = entry['name']

            if len(video_url) > 0:
                logger.debug('Successful to fetch video url from web page.')
                firefox.quit()
                break
            else:
                logger.debug('Failed to fetch video url from web page.')
                sleep(5)

            firefox.quit()

        # Check if we get the video url.
        if len(video_url) > 0:
            if len(download_file(video_url, str(Path(download_dir, filename + '.ts')), is_silent, referer_url=url)) == 0:
                return False
        else:
            logger.debug('Failed to get video url. The url is empty.')
            return False

    # Not supported website.
    else:
        print(f'The video from url "{url}" which is NOT supported.')
        logger.info(f'The video from url "{url}" which is NOT supported.')

        return False


    logger.debug(f'Trying to download video from the url......Done')
    return True


def interactive_mode(download_dir: str, is_silent: bool) -> bool:
    print(f'\n{BashColor.GREEN}[ New Case ]{BashColor.CLEAR}')

    url = input('Video url: ')

    if len(url) > 0:
        # Set filename.
        filename = input('\nDownloaded video filename: ')

        if len(filename) == 0:
            filename = None
        else:
            filename = Path(filename).name

        # Download video.
        is_success = download_video(url, download_dir, filename, is_silent=is_silent)

        # Check result.
        if is_success:
            print('Download video successfully.')
            logger.info('Download video successfully.')
        else:
            print('Download video failed.')
            logger.info('Download video failed.')

    return len(url) > 0


def batch_mode(download_dir: str, urls: List[str], is_silent: bool, validation_data: None | List[Dict[str,str|int|None]]) -> int:
    count_success = 0

    for i, url in enumerate(urls):
        print(f'\n{BashColor.GREEN}[ Case {i+1} ]{BashColor.CLEAR}')
        logger.info(f'[ Case {i+1} ]')

        # Download video.
        is_success = download_video(url, download_dir, is_silent=is_silent)

        # Check result.
        if is_success:
            if validation_data is not None:
                validation_datum = [datum for datum in validation_data if datum['url'] == url]
                validation_datum = validation_datum[0] if len(validation_datum) > 0 else None

                if validation_datum is not None:
                    validation_datum_filepath = validation_datum['filepath']
                    validation_datum_duration = validation_datum['duration']
                    validation_datum_size = validation_datum['size']

                    if validation_datum_filepath is not None and Path(validation_datum_filepath).is_file():
                        # Validate file size.
                        if Path(validation_datum_filepath).stat().st_size == validation_datum_size:
                            print(f'Validation success for field size with correct value "{validation_datum_size}".')
                            logger.info(f'Validation success for field size with correct value "{validation_datum_size}".')
                        else:
                            print(f'{BashColor.RED}Validation failed for field size with correct value "{validation_datum_size}".{BashColor.CLEAR}')
                            logger.info(f'Validation failed for field size with correct value "{validation_datum_size}".')

                        ffprobe = FFmpeg(executable='ffprobe').input(validation_datum_filepath, print_format='json', show_streams=None)

                        try:
                            media_meta = json.loads(ffprobe.execute())
                        except FFmpegError as e:
                            media_meta = {'streams': []}
                            logger.debug(f'Error occurred during video file meta retrieving. Here is the error message.\n{str(e).replace('\n', '\\n').replace('\r', '')}')

                        media_meta_durations = [meta['duration'] for meta in media_meta['streams'] if 'duration' in meta]

                        # Do stream data validations.
                        if 'streams' in media_meta:
                            # Validate duration.
                            if len(media_meta_durations) > 0 and media_meta_durations[0] == validation_datum_duration:
                                print(f'Validation success for field duration with correct value "{validation_datum_duration}".')
                                logger.info(f'Validation success for field duration with correct value "{validation_datum_duration}".')
                            else:
                                print(f'{BashColor.RED}Validation failed for field duration with correct value "{validation_datum_duration}".{BashColor.CLEAR}')
                                logger.info(f'Validation failed for field duration with correct value "{validation_datum_duration}".')

                    else:
                        print(f'{BashColor.RED}Validation failed for field filename with correct value "{validation_datum_filepath}".{BashColor.CLEAR}')
                        logger.info(f'Validation failed for field filename with correct value "{validation_datum_filepath}".')

                else:
                    print(f'No validation data provided for this case.')
                    logger.info(f'No validation data provided for this case.')

            print(f'Download video successfully.')
            logger.info(f'[ Case {i+1} ] Download video successfully.')
            count_success += 1

        else:
            print(f'Download video failed.')
            logger.info(f'[ Case {i+1} ] Download video failed.')

            # Write failed url to disk.
            with open(URL_FAILED_FILENAME, 'a') as fout:
                fout.write(url + '\n')

    print('\nAll cases are done.')
    print(f'{count_success}/{len(urls)} cases complete successfully.')

    if count_success != len(urls):
        print(f'{BashColor.RED}Urls failed to download are written to file "{URL_FAILED_FILENAME}" on disk.{BashColor.CLEAR}')

    logger.info('All cases are done.')
    logger.info(f'{count_success}/{len(urls)} cases complete successfully.')

    return count_success


def main():
    global logger

    # Check arguments.
    error_messages = []
    args_parser = get_args_parser()

    try:
        args = args_parser.parse_args()
    except argparse.ArgumentError as e:
        error_messages.append('Failed to parse argument.\n' + str(e).replace('\n', '\\n').replace('\r', ''))
    else:
        error_messages += check_args(args)

    if len(error_messages) > 0:
        print('\n'.join(error_messages))
        exit(1)

    # Initialize logger.
    logger = init_logger(args.work_dir)

    logger.debug(f'Parameter urls_path is set to "{args.urls_path}".')
    logger.debug(f'Parameter download_dir is set to "{args.download_dir}".')
    logger.debug(f'Parameter work_dir is set to "{args.work_dir}".')
    logger.debug(f'Parameter is_silent is set to "{args.is_silent}".')
    logger.debug(f'Parameter self_test is set to "{args.self_test}".')

    # Change working directory.
    if args.work_dir is not None:
        chdir(args.work_dir)

    # Interactive mode.
    if (args.self_test is None or not args.self_test) and (args.urls_path is None or len(args.urls_path) == 0):
        print('+--------------------------------+')
        print('|                                |')
        print('|  ' + BashColor.RED + 'Porn Video Downloader' + BashColor.CLEAR + '         |')
        print('|                                |')
        print('+--------------------------------+')
        print('|  ' + BashColor.GREEN + 'Supported Sites:' + BashColor.CLEAR + '              |')
        print('|    https://85po.com/           |')
        print('|    https://porn5f.com/         |')
        print('|    https://xvideos.com/        |')
        print('|    https://tktube.com/         |')
        print('|    https://missav.com/         |')
        print('|    https://iwant-sex.com/      |')
        print('+--------------------------------+')

        # Get download directory.
        download_dir = ''

        if args.download_dir is not None:
            download_dir = args.download_dir
        else:
            while download_dir is None or len(download_dir) == 0:
                download_dir = input('\nDirectory to save downloaded videos [default=./]: ')

                if len(download_dir) == 0:
                    download_dir = './'

                if not Path(download_dir).is_dir():
                    download_dir = ''
                    print('Directory must be existed.')

        print(f'\nDirectory to save downloaded videos: "{download_dir}".')
        logger.info(f'Parameter download_dir is set to "{download_dir}" manually.')

        while interactive_mode(download_dir, args.is_silent):
            pass

    # Batch mode.
    else:
        if args.self_test:
            std = self_test_data()
            urls = [datum['url'] for datum in std]
        else:
            std = None

            with open(args.urls_path) as fin:
                urls = fin.readlines()

            print(f'{len(urls)} urls loaded from file "{args.urls_path}".')
            logger.info(f'{len(urls)} urls loaded from file "{args.urls_path}".')

        urls = format_url_list(urls)

        print(f'{len(urls)} urls are filtered and accepted.')
        logger.info(f'{len(urls)} urls are filtered and accepted.')

        batch_mode(args.download_dir, urls, args.is_silent, std)

    clear_selenium_files()


'''
Main
'''

# Global variable.
logger: logging.Logger | None = None

if __name__ == '__main__':
    main()
