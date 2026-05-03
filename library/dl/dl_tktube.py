
from pathlib import Path

from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from library.dl.dl_base import DlBase
from library.web_driver import WebDriver


class DlTktube(DlBase):
    @staticmethod
    def get_domain() -> str:
        return 'tktube.com'

    def _get_video_url(self, url: str, output_title: str) -> Path | None:
        with WebDriver() as web_driver:
            web_driver.get(url)
            show_video_button = web_driver.find_element(By.CSS_SELECTOR, '.fp-ui')

            if show_video_button is None:
                return None

            web_driver.driver.execute_script('arguments[0].click();', show_video_button)

            try:
                WebDriverWait(web_driver.driver, 60).until(
                    expected_conditions.presence_of_element_located((By.CSS_SELECTOR, "video[src*='/get_file/']"))
                )
            except (NoSuchElementException, TimeoutException):
                return None

            video_element = web_driver.find_element(By.CSS_SELECTOR, "video[src*='/get_file/']")

            if video_element is None:
                return None

            video_url = video_element.get_attribute('src')

        if video_url is None:
            return None

        return self.download_video(video_url, output_title + '.mp4', url)
