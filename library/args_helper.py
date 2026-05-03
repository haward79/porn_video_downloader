
from argparse import ArgumentParser, Namespace, ArgumentError
from pathlib import Path
from typing import List

from library.log_helper import logger
from library.util import make_oneline_error_message


def get_args_parser() -> ArgumentParser:
    parser = ArgumentParser(description='Download porn videos. '
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


def check_args(args: Namespace) -> List[str]:
    error_messages = []

    if args.urls_path is not None and not Path(args.urls_path).is_file():
        error_messages.append('--urls-file parameter error: must be a FILE')

    if args.download_dir is not None and not Path(args.download_dir).is_dir():
        error_messages.append('--download-dir parameter error: must be a existed DIRECTORY')

    if args.work_dir is not None and not Path(args.work_dir).is_dir():
        error_messages.append('--work-dir parameter error: must be a existed DIRECTORY')

    return error_messages


def parse_args() -> Namespace | List[str]:
    error_messages = []

    try:
        args = get_args_parser().parse_args()
    except ArgumentError as e:
        error_messages.append('Failed to parse argument: ' + make_oneline_error_message(str(e)))
        logger().error(error_messages)
        return error_messages

    error_messages += check_args(args)

    if len(error_messages) > 0:
        logger().error(error_messages)
        return error_messages

    logger().info(f'Parameter urls_path is set to "{args.urls_path}".')
    logger().info(f'Parameter download_dir is set to "{args.download_dir}".')
    logger().info(f'Parameter work_dir is set to "{args.work_dir}".')
    logger().info(f'Parameter is_silent is set to "{args.is_silent}".')
    logger().info(f'Parameter self_test is set to "{args.self_test}".')

    return args
