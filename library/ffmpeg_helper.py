
from pathlib import Path
from typing import Any

import ffmpeg
from ffmpeg.exceptions import FFMpegError, FFMpegExecuteError

from library.log_helper import logger
from library.util import make_oneline_error_message, make_request_header


def ffmpeg_media_info(filepath: Path) -> Any:
    try:
        media_info_json = ffmpeg.probe(filepath)

    except FFMpegError as e:
        logger().error(
            'Error occurred during video file meta retrieving. ' +
            'Here is the error message. ' +
            make_oneline_error_message(str(e))
        )
        return None

    return media_info_json


def download_m3u8(
    url: str,
    filepath: Path,
    referer_url: str = '',
    show_progress: bool = False
) -> Path | None:
    headers = '\r\n'.join(
        f'{key}: {value}'
        for key, value in make_request_header(url, referer_url).items()
    )

    stream = (
        ffmpeg
            .input(url, extra_options={'headers': headers})
            .output(filename=str(filepath), vcodec='copy', acodec='copy')
            .global_args(y=True, loglevel='error', progress='pipe:1')
    )

    try:
        if show_progress:
            process = stream.run_async(pipe_stdout=True)

            if process.stdout is None:
                raise FFMpegExecuteError(
                    retcode=1,
                    cmd=stream.compile_line(),
                    stdout=b'',
                    stderr=b'stdout in None captured',
                )

            progress: dict[str, str] = {}

            for raw_line in process.stdout:
                key, _, value = raw_line.decode(errors='replace').strip().partition('=')

                if not key:
                    continue

                progress[key] = value

                if key == 'progress':
                    print('\rDownload Playlist: ' + str(progress), end='')
                    logger().debug('Download Playlist: ' + str(progress))

            return_code = process.wait()

            if return_code:
                raise FFMpegExecuteError(
                    retcode=return_code,
                    cmd=stream.compile_line(),
                    stdout=b'',
                    stderr=b'ffmpeg has completed but returned non-zero code',
                )

            print('\rDownload Playlist: Complete')

        else:
            stream.run()

    except FFMpegError as e:
        logger().error(
            'Error occurred during m3u8 downloading. ' +
            'Here is the error message. ' +
            make_oneline_error_message(str(e))
        )
        return None

    return filepath
