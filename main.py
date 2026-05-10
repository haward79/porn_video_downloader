
from argparse import Namespace
from typing import List
from pathlib import Path
from sys import exit
from os import chdir

from library.args_helper import parse_args
from library.dl.dl_base import DlBase
from library.log_helper import logger, stdout, init_logger
from library.test.test_case import TestCase
from library.util import format_url_list, BashColor


URL_FAILED_FILENAME = 'url_failed.txt'


def interactive_mode_download_dir() -> str:
    download_dir = ''

    while not download_dir:
        download_dir = input('\nDirectory to save downloaded videos [default=./]: ')

        if len(download_dir) == 0:
            download_dir = './'

        if not Path(download_dir).is_dir():
            download_dir = ''
            print('Directory must be a existed directory')

    return download_dir


def interactive_mode(download_dir: str, is_silent: bool) -> bool:
    print(f'\n{BashColor.GREEN}[ New Case ]{BashColor.CLEAR}')

    url = input('Video url: ')

    if not url:
        return False

    downloader = DlBase.determine_downloader(url)

    if downloader is None:
        msg = f'NOT supported url: "{url}"'
        logger().error(msg)
        stdout(msg)
        return True

    filename = input('\nDownloaded video filename: ')

    if filename:
        filename = Path(filename).name

    downloader_instance = downloader(Path(download_dir), is_silent)
    downloaded_filepath = downloader_instance.download(url, filename)

    if downloaded_filepath is None:
        msg = 'Download video failed'
    else:
        msg = f'Download video successfully: {downloaded_filepath}'

    logger().info(msg)
    stdout(msg)

    return True


def interactive_mode_wrapper(args: Namespace) -> bool:
    if args.download_dir:
        download_dir = args.download_dir
    else:
        download_dir = interactive_mode_download_dir()

    print(f'\nDirectory to save downloaded videos: {download_dir}')
    logger().info(f'Parameter download_dir is set to "{download_dir}" through stdio manually')

    while interactive_mode(download_dir, args.is_silent):
        pass  # NOSONAR

    return True


def batch_mode_download(
    case_id: int,
    download_dir: str,
    url: str,
    is_silent: bool,
    is_self_testing: bool,
) -> Path | None:
    print(f'\n{BashColor.GREEN}[ Case {case_id} ]{BashColor.CLEAR}')
    logger().info(f'[ Case {case_id} ]')

    downloader = DlBase.determine_downloader(url)

    if downloader is None:
        msg = f'[ Case {case_id} ] NOT supported url: "{url}"'
        logger().error(msg)
        stdout(msg)
        return None

    downloader_instance = downloader(Path(download_dir), is_silent)
    downloaded_filepath = downloader_instance.download(url)

    if downloaded_filepath is not None:
        return downloaded_filepath

    msg = f'[ Case {case_id} ] Video download failed'
    logger().error(msg)
    stdout(msg)

    if is_self_testing:
        return None

    with open(URL_FAILED_FILENAME, 'a') as f:
        f.write(url + '\n')

    return None


def batch_mode_validate(
    case_id: int,
    downloaded_filepath: Path,
    url: str,
    validation_data: List[TestCase],
) -> bool:
    validator = next(iter([datum for datum in validation_data if datum.url == url]), None)

    if validator is None:
        msg = f'[ Case {case_id} ] Validation data is NOT found for url "{url}"'
        logger().error(msg)
        stdout(msg)
        return False

    if validator.validate(downloaded_filepath):
        msg = f'[ Case {case_id} ] Validation successfully for url "{url}"'
        logger().info(msg)
        stdout(msg)
        return True

    msg = f'[ Case {case_id} ] Validation FAILED for url "{url}"'
    logger().info(msg)
    stdout(msg)
    return False


def batch_mode(download_dir: str, urls: List[str], is_silent: bool, validation_data: List[TestCase]) -> int:
    self_test_mode = len(validation_data) > 0
    success_count = 0

    for i, url in enumerate(urls):
        downloaded_filepath = batch_mode_download(
            i+1,
            download_dir,
            url,
            is_silent,
            self_test_mode,
        )

        if downloaded_filepath is None:
            continue

        if self_test_mode:
            if batch_mode_validate(
                i + 1,
                downloaded_filepath,
                url,
                validation_data,
            ):
                success_count += 1

            continue

        success_count += 1
        msg = f'[ Case {i + 1} ] Video download successfully: {downloaded_filepath}'
        logger().info(msg)
        stdout(msg)

    logger().info('\nAll cases are done')
    logger().info(f'{success_count}/{len(urls)} cases complete successfully')

    print('\nAll cases are done')
    print(f'{success_count}/{len(urls)} cases complete successfully')

    if not self_test_mode and success_count != len(urls):
        print(f'{BashColor.RED}URLs failed to download are written to file "{URL_FAILED_FILENAME}" on disk.{BashColor.CLEAR}')

    return success_count


def batch_mode_wrapper(args: Namespace) -> bool:
    test_cases = []

    if args.self_test:
        test_cases = TestCase.from_yml()
        urls = [
            case.url
            for case in test_cases
            if case.enabled
            if case.url is not None
        ]
    else:
        if not Path(args.urls_path).is_file():
            msg = f'Parameter urls_path is set to "{args.urls_path}" which is NOT a file'
            logger().error(msg)
            stdout(msg)
            return False

        with open(args.urls_path) as fin:
            urls = fin.readlines()

        msg = f'{len(urls)} urls loaded from file "{args.urls_path}"'
        logger().info(msg)
        stdout(msg)

    urls = format_url_list(urls)

    msg = f'{len(urls)} urls are filtered and accepted'
    logger().info(msg)
    stdout(msg)

    return batch_mode(args.download_dir, urls, args.is_silent, test_cases) == len(urls)


def main() -> bool:
    args = parse_args()

    if not isinstance(args, Namespace):
        msg = 'Failed to parse arguments'
        logger().error(msg)
        stdout(msg)
        return False

    init_logger(args.work_dir)

    logger().info(f'Parameter urls_path is set to "{args.urls_path}"')
    logger().info(f'Parameter download_dir is set to "{args.download_dir}"')
    logger().info(f'Parameter work_dir is set to "{args.work_dir}"')
    logger().info(f'Parameter is_silent is set to "{args.is_silent}"')
    logger().info(f'Parameter self_test is set to "{args.self_test}"')

    # Change working directory
    if args.work_dir is not None:
        chdir(args.work_dir)

    if not args.self_test and not args.urls_path:
        is_success = interactive_mode_wrapper(args)
    else:
        is_success = batch_mode_wrapper(args)

    return is_success


if __name__ == '__main__':
    exit(0 if main() else 1)
