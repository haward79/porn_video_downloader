
import json
from pathlib import Path
from typing import Any
from ffmpeg import FFmpeg
from ffmpeg import Progress as FFmpegProgress
from ffmpeg.errors import FFmpegError

from library.log_helper import logger, stdout
from library.util import make_oneline_error_message, make_request_header


def ffmpeg_media_info(filepath: str) -> Any:
    try:
        ffprobe = FFmpeg(executable='ffprobe').input(filepath, print_format='json', show_streams=None)
        media_info = ffprobe.execute()
        media_info_json = json.loads(media_info)

    except FFmpegError as e:
        logger().warning(f'Error occurred during video file meta retrieving. Here is the error message. {make_oneline_error_message(str(e))}')
        return None

    return media_info_json


def download_m3u8(url: str, filepath: Path, referer_url: str = '', show_progress: bool = False) -> Path | None:
    headers = '\r\n'.join(
        f'{key}: {value}'
        for key, value in make_request_header(url, referer_url).items()
    )

    ffmpeg = (
        FFmpeg()
        .option('y')
        .input(url, headers=headers)
        .output(
            str(filepath),
            vcodec='copy',
            acodec='copy'
        )
    )

    @ffmpeg.on('progress')
    def update_progress(progress: FFmpegProgress):
        if show_progress:
            stdout('\rDownload Playlist: ' + str(progress), end='')
            logger().debug('Download Playlist: ' + str(progress))

    ffmpeg.execute()

    if show_progress:
        stdout('\rDownload Playlist: Complete')

    return filepath
