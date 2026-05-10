
from pathlib import Path
from selenium.webdriver.common.by import By

from library.dl.dl_base import DlBase
from library.web_driver import WebDriver


class DlTktube(DlBase):
    @staticmethod
    def get_domain() -> str:
        return 'tktube.com'

    def _get_video_url(self, url: str, output_title: str) -> Path | None:
        with WebDriver() as web_driver:
            web_driver.get(url)
            show_video_button = web_driver.find_element(
                By.CSS_SELECTOR,
                '.fp-ui',
                self.SELENIUM_FIND_TIMEOUT
            )

            if show_video_button is None:
                return None

            web_driver.driver.execute_script('arguments[0].click();', show_video_button)

            video_element = web_driver.find_element(
                By.CSS_SELECTOR,
                "video[src*='/get_file/']",
                self.SELENIUM_FIND_TIMEOUT
            )

            if video_element is None:
                return None

            video_url = video_element.get_attribute('src')

        if video_url is None:
            return None

        return self.download_video(video_url, output_title + '.mp4', url)
