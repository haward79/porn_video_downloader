
# Import library.
from typing import List
import logging
import argparse
from pathlib import Path
from os import popen
from math import ceil
from time import sleep
import urllib
import urllib3
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, InvalidArgumentException, WebDriverException

# Disable urllib TLS certificate warning.
urllib3.disable_warnings()


# Define constant.
URL_FAILED_FILENAME = 'url_failed.txt'
SIZE_NAMES = ('B', 'KB', 'MB', 'GB', 'TB')
REQUEST_HEADER = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0'}
REQUEST_CHUNK_SIZE = 4096
MAX_FILENAME_LENGTH = 90


# Define class.
class BashColor:

    # Constants.
    CLEAR = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'


# Define function.
def init_logger(work_dir: str) -> logging.Logger:

    filename = Path(work_dir, 'CHECKME.log')
    logging.basicConfig(filename=filename, level=logging.CRITICAL, format='%(asctime)s|%(levelname)s|%(message)s')

    logger = logging.getLogger('porn_video_downloader')
    logger.setLevel(logging.DEBUG)

    logger.debug('Logging start')

    return logger


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

    return parser


def check_args(args: argparse.Namespace) -> None:

    if args.urls_path is not None:
        if not Path(args.urls_path).is_file():
            print('--urls-file parameter error: must be a FILE')
            exit(1)

    if args.download_dir is not None:
        if not Path(args.download_dir).is_dir():
            print('--download-dir parameter error: must be a existed DIRECTORY')
            exit(1)

    if not Path(args.work_dir).is_dir():
        print('--work-dir parameter error: must be a existed DIRECTORY')
        exit(1)


def get_terminal_size() -> dict:

    rows = 0
    cols = 0

    try:
        (rows, cols) = popen('stty size').read().split()
    except:
        print('Failed to get size of terminal.')
    else:
        rows = int(rows)
        cols = int(cols)

    return {'row': rows, 'col': cols}


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


def url_list_format(urls: List[str]) -> List[str]:

    urls = urls.copy()

    for i in range(len((urls))):
        if urls[i].endswith('\r\n') or urls[i].endswith('\n\r'):
            urls[i] = urls[i][:-2]
        elif urls[i].endswith('\r') or urls[i].endswith('\n'):
            urls[i] = urls[i][:-1]

    urls = [url for url in urls if len(url) > 0]

    return urls


def get_max_resolution_url(urls: List[str]) -> str:

    logger.debug('Checking max resolution segment.')
    resolutions = []

    for i, url in enumerate(urls):
        start_index = url.find('hls-')

        if start_index != -1:
            start_index += 4
            resolution = fetch_string(url, start_index, 'p')

            if len(resolution) > 0:
                resolution = int(resolution)
                resolutions.append(resolution)

    if len(resolutions) > 0:
        if len(resolutions) == len(list(set(resolutions))):
            resolutions.sort(reverse=True)
            target_resolution = 'hls-' + str(resolutions[0]) + 'p'

            for url in urls:
                if url.find(target_resolution) != -1:
                    logger.debug(f'Max resolution is set to url "{url}".')
                    logger.debug('Checking max resolution segment......Done')
                    return url

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
    firefox_options.add_argument('-headless')

    firefox = webdriver.Firefox(options=firefox_options)

    return firefox


def clear_selenium_files() -> None:

    logger.debug('Removing geckodriver log file.')

    log = Path('geckodriver.log')

    if log.is_file():
        log.unlink()
        logger.debug('Removed geckodriver log file.')

    logger.debug('Removing geckodriver log file......Done')


def selenium_get_url(firefox: webdriver.firefox.webdriver.WebDriver, url: str) -> bool:

    try:
        logger.debug(f'Loading url "{url}" .')
        firefox.get(url)

    except InvalidArgumentException as e:
        logger.debug(f'Invalid url "{url}".')
        return False

    except WebDriverException as e:
        # A DNS error.
        if str(e).find('neterror?e=dnsNotFound') != -1:
            logger.debug('DNS related error occurred. It may due to too many concurrent connection to your DNS server.')
            return selenium_get_url(firefox, url)

        # NOT an DNS error.
        else:
            logger.debug(f'Error occurred. Here is the error message.\n{str(e)}')
            return False

    return True


def selenium_load_url(url: str, preload_times: int = 0) -> webdriver.firefox.webdriver.WebDriver:

    firefox = create_selenium_instance()

    # Preload url.
    if preload_times >= 0:
        logger.debug('Do preload......')

        for i in range(preload_times):
            logger.debug(f'Do preload......{i+1}/{preload_times}')

            if selenium_get_url(firefox, url):
                logger.debug(f'Do preload......{i + 1}/{preload_times} Success')
            else:
                logger.debug(f'Do preload......{i + 1}/{preload_times} Failed')

            sleep(1)

        logger.debug('Do preload......Done')

    else:
        print('Invalid parameter: preload_times should be a integer equal or greater than 0.')
        logger.info('Invalid parameter: preload_times should be a integer equal or greater than 0.')
        firefox.quit()
        return

    # Formally load url.
    logger.debug(f'Formally load url "{url}" .')

    while not selenium_get_url(firefox, url):
        logger.debug(f'Failed to load url "{url}" formally. Keep trying.')

    return firefox


def get_website_code(url: str) -> str:

    if url.find('85tube.com') != -1:
        firefox = selenium_load_url(url, preload_times=5)
    else:
        firefox = selenium_load_url(url)

    if firefox is not None:
        source_code = firefox.page_source
        firefox.quit()

        logger.debug(f'Successfully get source code for the url.')

    else:
        source_code = ''

        logger.debug(f'Failed to get source code for the url due to previous error.')

    return source_code


def get_website_title(url: str) -> str:

    logger.debug(f'Try to get website title from the url "{url}".')

    source_code = get_website_code(url)
    start_index = source_code.find("<title>")

    if start_index == -1:
        return ""
    else:
        start_index += 7
        ending_index = source_code.find("</title>", start_index)

        if ending_index == -1:
            return ""
        else:
            website_title = source_code[start_index:ending_index]
            website_title = website_title.replace('.part', ' part')  # To prevent conflict with clip_filename().
            website_title = website_title.replace('/', '_')
            logger.debug(f'Got website title "{website_title}".')

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
                logger.debug(f'Error occurred. Here is the error message.\n{str(e)}')

            continue

        content_bytes = request.headers.get('content-length')

        # Format file size and output it.
        if content_bytes is None:
            if is_top:
                print('File size reported from server is unavailable.')
        else:
            content_bytes = int(content_bytes)

        logger.debug(f'File size reported from server is {content_bytes} bytes ().')

        # Clear download file.
        with open(filepath, "wb") as fout:
            pass

        '''
        Download file.
        '''
        # Download file with no message.
        if not is_top or is_silent or content_bytes is None:
            with open(filepath, "ab") as fout:
                fout.write(request.content)

        # Download file with progress message.
        else:
            downloaded_bytes = 0

            # Download data for chunk size at once.
            for slice_data in request.iter_content(chunk_size=REQUEST_CHUNK_SIZE):
                # Write chunk to disk.
                with open(filepath, "ab") as fout:
                    fout.write(slice_data)

                # Print progress bar.
                cols = get_terminal_size()['col'] - 15
                downloaded_bytes += len(slice_data)
                progress = downloaded_bytes / content_bytes
                progress_percent = int(progress * 100)
                bar_downloaded = int(cols * progress)
                bar_not_downloaded = cols - bar_downloaded
                print('\r[{}{}] {:3d}%'.format('=' * bar_downloaded, ' ' * bar_not_downloaded, progress_percent), end='')
                # logger.info(f'File downloaded for {downloaded_bytes} bytes in {content_bytes} bytes.')

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
            urls = url_list_format(urls)

            # Check if urls in playlist are different resolution.
            max_resolution_url = get_max_resolution_url(urls)

            logger.info(f'urls: {urls}')
            logger.info(f'max_resolution_url: {max_resolution_url}')

            if len(max_resolution_url) > 0:
                urls = [max_resolution_url,]

            # Fix playlist without full url.
            for i, url in enumerate(urls):
                if url.startswith('https://') or url.startswith('http://'):
                    pass
                else:
                    urls[i] = urllib.parse.urljoin(original_url, url)

            # Download all segments.
            filepath_base = filepath
            merge_files = []
            for i, url in enumerate(urls):
                logger.debug(f'Downloading segment part {i+1}.')
                filepath_subfile = download_file(url, filepath_base + '.part' + str(i+1), is_silent, False, referer_url)
                merge_files.append(filepath_subfile)
                logger.debug(f'Downloading segment part {i + 1}......Done')
                logger.debug(f'Segment file is saved to "{filepath_subfile}".')

                # Print progress bar.
                if is_top and not is_silent:
                    cols = get_terminal_size()['col'] - 15
                    progress = (i + 1) / len(urls)
                    progress_percent = int(progress * 100)
                    bar_downloaded = int(cols * progress)
                    bar_not_downloaded = cols - bar_downloaded
                    print('\r[{}{}] {:3d}%'.format('=' * bar_downloaded, ' ' * bar_not_downloaded, progress_percent), end='')

            if is_top and not is_silent:
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


def download_video(url: str, download_dir: str = None, filename: str = None, is_silent: bool = False) -> bool:

    logger.debug(f'Trying to download video from the url.')
    logger.debug(f'with parameter url: {url}')
    logger.debug(f'with parameter download_dir: {download_dir}')
    logger.debug(f'with parameter filename: {filename}')
    logger.debug(f'with parameter is_silent: {is_silent}')

    # Set download directory to current working directory by default.
    if download_dir is None or len(download_dir) == 0:
        download_dir = './'

    logger.debug(f'parameter download_dir is set to "{download_dir}".')

    # Get filename from website title by default.
    if filename is None or len(filename) == 0:
        filename = get_website_title(url)

        if len(filename) == 0:
            print('Failed to get website title as filename.')
            logger.info('Failed to get website title as filename.')

            return False

    # Get filename with no extension.
    else:
        filename = Path(filename).stem

    logger.debug(f'parameter filename is set to "{filename}".')


    '''
    Download video.
    '''

    # It's from 85tube.com .
    if url.find('85tube.com') != -1:
        logger.debug('It\'s a url from 85tube.')
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
        pos = source_code.find('source src="')

        if pos != -1:
            video_url = fetch_string(source_code, pos + 12, '"')

        # Check if we get the video url.
        if len(video_url) > 0 and video_url.find('porn5f.com') != -1:
            video_url = video_url.replace('&amp;', '&')
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
            WebDriverWait(firefox, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'video[src*=\'tktube.com/get_file/\']')))
            video = firefox.find_element(By.CSS_SELECTOR, 'video[src*=\'tktube.com/get_file/\']')
            video_url = video.get_attribute('src')

        except:
            logger.debug('Failed to get video url. Exception occurred.')
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

        # Fetch video url.
        firefox = selenium_load_url(url)

        entries = firefox.execute_script('return window.performance.getEntries();')

        for entry in entries:
            if entry['name'].find('.m3u8') != -1:
                video_url = entry['name']

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

    url = input('Please input a supported video url: ')

    if len(url) > 0:
        filename = input('\nPlease input filename: ')

        if len(filename) == 0:
            filename = None
        else:
            filename = Path(filename).name

        is_success = download_video(url, download_dir, filename, is_silent=is_silent)

        if is_success:
            print('Download video successfully.')
            logger.info('Download video successfully.')

        else:
            print('Download video failed.')
            logger.info('Download video failed.')

    return len(url) > 0


def batch_mode(download_dir: str, urls: List[str], is_silent: bool) -> None:

    count_success = 0

    for i, url in enumerate(urls):
        print(f'\n{BashColor.GREEN}[ Case {i+1} ]{BashColor.CLEAR}')
        logger.info(f'[ Case {i+1} ]')

        is_success = download_video(url, download_dir, is_silent=is_silent)

        if is_success:
            print(f'Download video successfully.')
            logger.info(f'[ Case {i+1} ] Download video successfully.')
            count_success += 1
        else:
            print(f'Download video failed.')
            logger.info(f'[ Case {i+1} ] Download video failed.')

            # Write failed url to disk.
            with open(URL_FAILED_FILENAME, 'a') as fout:
                fout.write(url + '\n')
            print('This url failed to download is written to disk.')
            logger.info('This url failed to download is written to disk.')

    print('\nAll cases done.')
    print(f'{count_success}/{len(urls)} cases complete successfully.')
    print(f'Urls failed to download are written to file "{URL_FAILED_FILENAME}" on disk.')

    logger.info('All cases done.')
    logger.info(f'{count_success}/{len(urls)} cases complete successfully.')


'''
Main
'''
# Check arguments.
args_parser = get_args_parser()
try:
    args = args_parser.parse_args()
except argparse.ArgumentError as e:
    print('Failed to parse argument.')
else:
    check_args(args)

# Initialize logger.
logger = init_logger(args.work_dir)


if __name__ == '__main__':
    logger.debug(f'Parameter urls_path is set to "{args.urls_path}".')
    logger.debug(f'Parameter download_dir is set to "{args.download_dir}".')
    logger.debug(f'Parameter work_dir is set to "{args.work_dir}".')

    # Interactive mode.
    if args.urls_path is None:
        print('+------------------------------+')
        print('|                              |')
        print('|  ' + BashColor.RED + 'Porn Video Downloader' + BashColor.CLEAR + '       |')
        print('|                              |')
        print('+------------------------------+')
        print('|  ' + BashColor.GREEN + 'Supported Sites:' + BashColor.CLEAR + '            |')
        print('|    https://85tube.com/       |')
        print('|    https://porn5f.com/       |')
        print('|    https://xvideos.com/      |')
        print('|    https://tktube.com/       |')
        print('|    https://missav.com/       |')
        print('+------------------------------+')

        # Get download directory.
        download_dir = ''

        if args.download_dir is not None:
            download_dir = args.download_dir

        else:
            while len(download_dir) == 0:
                download_dir = input('\nPlease input download directory: ')

                if len(download_dir) == 0:
                    download_dir = './'

                if not Path(download_dir).is_dir():
                    download_dir = ''
                    print('Download directory must be a existed directory.')

        print(f'\nDownload directory is set to "{download_dir}".')
        logger.info(f'Parameter download_dir is set to "{download_dir}" manually.')

        while interactive_mode(download_dir, args.is_silent):
            pass

    # Batch mode.
    else:
        with open(args.urls_path) as fin:
            urls = fin.readlines()
        urls = url_list_format(urls)

        print(f'{len(urls)} urls loaded from file "{args.urls_path}".')
        logger.info(f'{len(urls)} urls loaded from file "{args.urls_path}".')

        batch_mode(args.download_dir, urls, args.is_silent)

    clear_selenium_files()
