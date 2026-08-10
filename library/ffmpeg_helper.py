
from pathlib import Path
from typing import Any

import ffmpeg
from ffmpeg.exceptions import FFMpegError, FFMpegExecuteError

from library.log_helper import logger, stdout
from library.util import make_oneline_error_message, make_request_header


def ffmpeg_media_info(filepath: Path) -> Any:
    try:
        media_info_json = ffmpeg.probe(filepath)

    except FFMpegError as e:
        logger().exception(
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
            .output(filename=filepath, vcodec='copy', acodec='copy')
            .global_args(y=True, loglevel='error', progress='pipe:1')
    )

    try:
        process = stream.run_async(pipe_stdout=True, pipe_stderr=True)

        if process.stdout is None or process.stderr is None:
            raise FFMpegExecuteError(
                retcode=1,
                cmd=stream.compile_line(),
                stdout=b'',
                stderr=b'stdout in None captured',
            )

        progress_str = ''

        for raw_line_bytes in process.stdout:
            raw_line = raw_line_bytes.decode(errors='replace').strip()
            key, _, _ = raw_line.partition('=')
            progress_str += raw_line + ' '

            if show_progress:
                stdout('\r' + progress_str, end='')

            if key == 'progress':
                logger().debug(progress_str)
                progress_str = ''

        # End of the progress output
        if show_progress:
            stdout()

        return_code = process.wait()

        if return_code:
            raise FFMpegExecuteError(
                retcode=return_code,
                cmd=stream.compile_line(),
                stdout=b'',
                stderr=b'ffmpeg has completed but returned non-zero code',
            )

    except FFMpegError as e:
        logger().exception(
            'Error occurred during m3u8 downloading. ' +
            'Here is the error message. ' +
            make_oneline_error_message(str(e))
        )
        return None

    if not filepath.is_file() or filepath.stat().st_size == 0:
        filepath.unlink(missing_ok=True)
        logger().error(
            f'Downloaded m3u8 file "{filepath}" NOT found or is EMPTY. ' +
            'This may due to remote sent nothing or no write permission to file.'
        )
        return None

    return filepath
