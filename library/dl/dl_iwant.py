
from pathlib import Path
from typing import Any, cast

from library.dl.dl_base import DlBase
from library.web_driver import WebDriver


class DlIwant(DlBase):
    @staticmethod
    def get_domain() -> str:
        return 'iwant-sex.com'

    def _get_video_url(self, url: str, output_title: str) -> Path | None:
        with WebDriver() as web_driver:
            web_driver.get(url)

            entries = cast(
                'list[dict[str, Any]]',
                web_driver.driver.execute_script('return window.performance.getEntries();'),  # pyright: ignore[reportUnknownMemberType]
            )

            for entry in entries:
                video_url = str(entry['name'])

                if video_url.find('.m3u8') != -1:
                    return self.download_video(video_url, output_title + '.mp4', url)

        return None
