
from pathlib import Path
from typing import List
import yaml

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
