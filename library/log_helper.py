
import logging
from pathlib import Path


def stdout(*args, **kwargs) -> None:
    print(*args, **kwargs, flush=True)


def logger() -> logging.Logger:
    if __logger_instance is None:
        raise Exception('Logger not initialized.')

    return __logger_instance


def init_logger(work_dir: str) -> None:
    global __logger_instance

    filename = Path(work_dir, 'CHECKME.log')
    logging.basicConfig(
        filename=filename,
        level=logging.CRITICAL,
        format='%(asctime)s|%(levelname)s|%(message)s'
    )

    logger_instance = logging.getLogger('porn_video_downloader')

    logger_instance.setLevel(logging.DEBUG)
    logger_instance.debug('Logging start')

    __logger_instance = logger_instance


__logger_instance: logging.Logger | None = None
