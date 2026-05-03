
from pathlib import Path

from library.dl.dl_base import DlBase


class DlFiveF(DlBase):
    @staticmethod
    def get_domain() -> str:
        return 'porn5f.com'

    def _download(self, url: str, output_title: str = '') -> Path | None:
        pass

    def get_title(self, url: str) -> str:
        pass
