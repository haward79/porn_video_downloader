
from pathlib import Path

from library.dl.dl_base import DlBase
from library.web_driver import WebDriver


class DlIwant(DlBase):
    @staticmethod
    def get_domain() -> str:
        return 'iwant-sex.com'

    def _get_video_url(self, url: str, output_title: str) -> Path | None:
        with WebDriver() as web_driver:
            web_driver.get(url)

            entries = web_driver.driver.execute_script('return window.performance.getEntries();')

            for entry in entries:
                if entry['name'].find('.m3u8') != -1:
                    video_url = entry['name']
                    return self.download_video(video_url, output_title + '.mp4')

        return None
