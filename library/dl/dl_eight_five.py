
from pathlib import Path

from selenium.webdriver.common.by import By

from library.dl.dl_base import DlBase
from library.web_driver import WebDriver


class DlEightFive(DlBase):
    @staticmethod
    def get_domain() -> str:
        return '85po.com'

    def _get_video_url(self, url: str, output_title: str) -> Path | None:
        with WebDriver() as web_driver:
            web_driver.get(url)

            video_element = web_driver.find_element(By.CSS_SELECTOR, '#kt_player video')

            if video_element is None:
                return None

            video_url = video_element.get_attribute('src')

        if video_url is None:
            return None

        return self.download_video(video_url, output_title + '.mp4')
