
from pathlib import Path
from typing import List
import yaml

from library.ffmpeg_helper import ffmpeg_media_info
from library.log_helper import logger


class TestCase:
    @staticmethod
    def from_yml(_file: Path | None = None) -> List['TestCase']:
        if _file is None:
            file = Path('test_cases.yml')
        else:
            file = _file

        if not file.is_file():
            logger().error(f'File for test cases "{file}" NOT found')
            return []

        with open(file, 'r') as fin:
            data = yaml.safe_load(fin)

        if not isinstance(data, list):
            return []

        return [TestCase(**datum) for datum in data]

    def __init__(
        self,
        url: str | None = None,
        filepath: Path | None = None,
        duration: float = -1,
        size: int = -1,
        enabled: bool = False,
    ):
        self.__url: str | None =url
        self.__filepath: Path | None =filepath
        self.__duration: float = duration
        self.__size: int = size
        self.__enabled: bool = enabled

    def validate(self, target: Path) -> bool:
        if not target.is_file():
            logger().error(f'Validation stop for other fields due to output file "{target}" NOT found')
            return False

        has_failed = False

        if self.filepath is None or (self.filepath.is_file() and self.filepath == target):
            logger().info(f'Validation success for field "filepath" with correct value "{self.filepath}"')
        else:
            logger().error(f'Validation failed for field "filepath" with expected "{self.filepath}" but got "{target}"')
            has_failed = True

        file_size = target.stat().st_size

        if self.size > 0 or file_size == self.size:
            logger().info(f'Validation success for field "size" with correct value "{self.size}"')
        else:
            logger().error(f'Validation failed for field "size" with expected "{self.size}" but got "{file_size}"')
            has_failed = True

        media_meta = ffmpeg_media_info(target)

        if media_meta is None or 'streams' not in media_meta:
            has_failed = True
        else:
            media_duration = next(iter([
                float(meta['duration'])
                for meta in media_meta['streams']
                if 'duration' in meta
            ]), -1)

            if self.duration > 0 or media_duration == self.duration:
                logger().info(f'Validation success for field "duration" with correct value "{self.duration}"')
            else:
                logger().error(f'Validation failed for field "duration" with expected "{self.duration}" but got "{media_duration}"')
                has_failed = True

        return not has_failed

    @property
    def url(self) -> str | None:
        return self.__url

    @property
    def filepath(self) -> Path | None:
        return self.__filepath

    @property
    def duration(self) -> float:
        return self.__duration

    @property
    def size(self) -> int:
        return self.__size

    @property
    def enabled(self) -> bool:
        return self.__enabled
