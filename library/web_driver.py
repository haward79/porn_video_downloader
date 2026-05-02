
from pathlib import Path
import requests
from os import environ
from selenium.webdriver.firefox.webdriver import WebDriver as SeleniumWebDriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.relative_locator import RelativeBy


class WebDriver:
    @staticmethod
    def create_web_driver() -> SeleniumWebDriver:
        if (sh_env := environ.get('SELENIUM_HEADLESS')) and str(sh_env).lower() == 'false':
            return SeleniumWebDriver()

        options = Options()
        options.add_argument("--headless")

        firefox = SeleniumWebDriver(options=options)
        firefox.set_page_load_timeout(60)

        return firefox

    @staticmethod
    def clear_web_driver_logs() -> None:
        log = Path('geckodriver.log')

        if log.is_file():
            log.unlink(missing_ok=True)

    def __init__(self):
        self._driver: SeleniumWebDriver | None = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.quit()

    def _get_web_driver(self) -> SeleniumWebDriver:
        if self._driver:
            return self._driver

        self._driver = self.create_web_driver()

        assert(isinstance(self._driver, SeleniumWebDriver))

        return self._driver

    def _release_web_driver(self) -> None:
        if self._driver is None:
            return

        self._driver.quit()
        self._driver = None

        self.clear_web_driver_logs()

    def quit(self) -> None:
        self._release_web_driver()

    def fill_element(
        self,
        by: str | RelativeBy,
        selector: str,
        value: str,
    ) -> bool:
        element = self.driver.find_element(by, selector)

        if not isinstance(element, WebElement):
            return False

        element.send_keys(value)

        return True

    def click_element(
        self,
        by: str | RelativeBy,
        selector: str,
    ) -> bool:
        element = self.driver.find_element(by, selector)

        if not isinstance(element, WebElement):
            return False

        element.click()

        return True

    def to_requests(self) -> requests.Session:
        cookies = self.driver.get_cookies()

        session = requests.Session()

        for cookie in cookies:
            session.cookies.set(
                name=cookie['name'],
                value=cookie['value'],
                domain=cookie.get('domain'),
                path=cookie.get('path')
            )

        return session

    @property
    def driver(self) -> SeleniumWebDriver:
        return self._get_web_driver()
