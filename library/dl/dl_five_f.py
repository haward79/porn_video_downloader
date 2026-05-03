
from pathlib import Path
from bs4 import BeautifulSoup, Tag

from library.dl.dl_base import DlBase
from library.web_driver import WebDriver


class DlFiveF(DlBase):
    @staticmethod
    def get_domain() -> str:
        return 'porn5f.com'

    def _get_video_url(self, url: str, output_title: str) -> Path | None:
        with WebDriver() as web_driver:
            web_driver.get(url)
            source_code = web_driver.driver.page_source

        video_urls = [
            element_source_src
            for element in BeautifulSoup(source_code, 'html.parser').find_all('video')
            if isinstance(element, Tag)
            if isinstance(element_source := element.find('source'), Tag)
            if (element_source_src := element_source.attrs.get('src'))
            if isinstance(element_source_src, str)
            if element_source_src.find(self.get_domain()) != -1
        ]
        video_url = video_urls[0] if len(video_urls) > 0 else ''

        return self.download_video(video_url, output_title + '.mp4', url)
