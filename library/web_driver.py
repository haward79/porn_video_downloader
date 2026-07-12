
from time import sleep
from urllib.parse import urlparse
import requests
from os import environ
import undetected_chromedriver as uc
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.relative_locator import RelativeBy
from selenium.webdriver.support.wait import WebDriverWait

from library.log_helper import logger


class WebDriver:
    @staticmethod
    def create_web_driver() -> uc.Chrome:
        headless = not ((sh_env := environ.get('SELENIUM_HEADLESS')) and str(sh_env).lower() == 'false')

        chrome = uc.Chrome(headless=headless)
        chrome.set_page_load_timeout(60)

        return chrome

    def __init__(self):
        self._driver: uc.Chrome | None = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.quit()

    def _get_web_driver(self) -> uc.Chrome:
        if self._driver:
            return self._driver

        self._driver = self.create_web_driver()

        assert(isinstance(self._driver, uc.Chrome))

        return self._driver

    def _release_web_driver(self) -> None:
        if self._driver is None:
            return

        self._driver.quit()
        self._driver = None

    def quit(self) -> None:
        self._release_web_driver()

    def get(self, url: str, referer: str = '', pre_load: int = 0) -> None:
        if not referer:
            referer = urlparse(url).scheme + '://' + urlparse(url).netloc

        if pre_load < 0:
            pre_load = 0

        for i in range(pre_load + 1):
            if pre_load == i:
                logging_msg = f'Formal-loading for "{url}"'
            else:
                logging_msg = f'Pre-loading {i + 1} times for "{url}"'

            logger().debug(f"{logging_msg} ...")

            self.driver.get(referer)
            sleep(1)
            self.driver.get(url)

            logger().debug(f"{logging_msg} ... Done")

    def find_element(
        self,
        by: str | RelativeBy,
        selector: str,
        timeout: int = 0,
    ) -> WebElement | None:
        try:
            if timeout > 0:
                WebDriverWait(self.driver, timeout).until(
                    expected_conditions.presence_of_element_located((str(by), selector))
                )

            element = self.driver.find_element(str(by), selector)
        except (NoSuchElementException, TimeoutException):
            logger().error(f'Failed to locate element "{selector}" by "{by if isinstance(by, str) else by.__class__.__name__}".')
            return None

        return element

    def fill_element(
        self,
        by: str | RelativeBy,
        selector: str,
        value: str,
    ) -> bool:
        element = self.find_element(by, selector)

        if element is None:
            return False

        element.send_keys(value)

        return True

    def click_element(
        self,
        by: str | RelativeBy,
        selector: str,
    ) -> bool:
        element = self.find_element(by, selector)

        if element is None:
            return False

        element.click()

        return True

    def to_requests(self, visit_url: str | None = None) -> requests.Session:
        if visit_url:
            self.driver.get(visit_url)

        cookies = self.driver.get_cookies()

        session = requests.Session()

        for cookie in cookies:
            session.cookies.set(
                name=cookie['name'],
                value=cookie['value'],
                domain=cookie.get('domain'),
                path=cookie.get('path')
            )

        session.headers.update({'User-Agent': self.user_agent})

        return session

    @property
    def driver(self) -> uc.Chrome:
        return self._get_web_driver()

    @property
    def cookies(self) -> dict:
        return { c['name']: c['value'] for c in self.driver.get_cookies() }

    @property
    def user_agent(self) -> str:
        return self.driver.execute_script('return navigator.userAgent;')
