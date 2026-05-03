
from pathlib import Path

from library.dl.dl_base import DlBase
from library.util import extract_string
from library.web_driver import WebDriver


class DlXvideos(DlBase):
    @staticmethod
    def get_domain() -> str:
        return 'xvideos.com'

    def _get_video_url(self, url: str, output_title: str) -> Path | None:
        with WebDriver() as web_driver:
            web_driver.get(url)
            source_code = web_driver.driver.page_source

        pos = source_code.find('html5player.setVideoHLS')

        if pos == -1:
            return None

        video_url = extract_string(source_code, pos + 25, "'")

        return self.download_video(video_url, output_title + '.mp4', url)
