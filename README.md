# Overview

This is an **online video downloader** that
allows you to download videos from supported websites.

Currently, the program supports videos from the following websites:

- xvideos.com
- porn5f.com
- 85po.com
- tktube.com
- iwant-sex.com

# Specification

- Supports both **file input** and **keyboard input** for video URLs.
- Users can **select the download directory**.
- Automatically retrieves **web page titles** as video filenames.
- Videos are downloaded **serially** with a **retry-on-failure** mechanism.
- Displays **progress bars** during downloads.
- Supports **silent mode** with no extra output.
- Detailed **logging mechanism** included for easy debugging.

# Pre-requirements

## Software

- **Linux-based OS**  
  - *Note: This program may run on Windows by modifying some code.*
- **Python 3**
- **Python 3 Libraries**
  - See `uv tree` for a list of dependencies.
  - **Selenium** (web browser driver)  
    - Install the appropriate web browser and driver for Selenium (Python library).  
    - Reference: [Selenium PyPI](https://pypi.org/project/selenium/)
- **Web Browser** (with media codecs)  
  - Install codecs using `apt` with package name: `libavcodec-extra`
- **FFmpeg**  
  - Install using `apt` with package name: `ffmpeg`

## Hardware

There are **minimal hardware requirements** for this program.

- Most modern systems can run it without issues.
- Even a **Raspberry Pi 3** is sufficient.

# Install

This program does **not require a global installation**.

However, some Python dependencies are required.
You can install them using the following optional command
(it will also run automatically on first execution):

```bash
uv sync
```

# Usage

To view the help message, open a terminal and run:

```bash
uv run python Main.py -h
```

Then, follow the on-screen instructions to start using the program.

# Changelog

<details>

  <summary>Check long-long changelog</summary>

  - 04 / 13 2026
    - Replace pip with uv
    - Add syntax check to todo

  - 03 / 16 2026
    - Update gitlab-ci to sync with GitHub
    - Remove old pipelines for now

  - 04 / 30 2025
    - Update gitlab-ci

  - 02 / 04 2025
    - Update README
  
  - 02 / 04 2025
    - Fix bugs.
    - Add ffmpeg media transcode.
    - Remove missav.com support.
    - Add requirements.txt .
  
  - 02 / 02 2025
    - Fix bugs.
  
  - 02 / 01 2025
    - Fix bugs.
    - Add PreProcess module.
  
  - 01 / 30 2025
    - Fix bugs.
    - Use tqdm for progress bar.
    - Add iwant-sex.com support.
    - Add self test feature.
  
  - 05 / 23 2024
    - Remove support for 85tube.com .
    - Add support for 85po.com .
  
  - 02 / 19 2024
    - Fix bug for tktube.com .
  
  - 01 / 05 2024
    - Add future work section in README file.
  
  - 12 / 28 2023
    - Fix bug for videos from missav.com .
  
  - 04 / 29 2023
    - Fix bug for videos from missav.com .
  
  - 04 / 22 2023
    - Add DNS concurrent restriction catcher for requests library.
  
  - 04 / 22 2023
    - Add support for missav.com .
    - Add DNS concurrent restriction catcher for selenium.
  
  - 03 / 26 2023
    - Edit copyright.
  
  - 03 / 18 2023
    - Fix bugs for accumulated hidden firefoxes!!
  
  - 02 / 24 2023
    - Fix bug in get_max_resolution_url().
  
  - 02 / 13 2023
    - Fix bug in get_max_resolution_url().
  
  - 01 / 08 2023
    - Fix bug for filepath clipping in download_file().
  
  - 12 / 13 2022
    - Fix bugs for download_file().
    - Write chunk of data to disk to reduce memory usage. (I know disk write operation is slow. QAQ)
    - Write urls failed to download to disk.
  
  - 12 / 11 2022
    - Significant change on codes. All codes are rewrote.
    - .gitignore edited.
  
  - 11 / 24 2022
    - Replace deprecated function in selenium.
  
  - 06 / 09 2022
    - Fix bug for 85tube.com .
  
  - 06 / 09 2022
    - Fix bug for 85tube.com .
  
  - 06 / 05 2022
    - Fix bug for 85tube.com .
  
  - 04 / 26 2022
    - Fix bug for xvideos.com .
  
  - 03 / 29 2022
    - Fix bug for xvideos.com .
  
  - 11 / 07 2021
    - Fix bugs for porn5f.com .
    - Remove .gitignore from git management.
    - Edit Pre-requirements guide in README.md .
  
  - 07 / 18 2021
    - Remove use of urllib.
    - Add silent mode.
  
  - 07 / 04 2021
    - Remove unused import.
    - Improve download scripts for tktube.
    - Fix empty video url bug.
  
  - 06 / 25 2021
    - Add support for tktube.com .
    - Add module support for this library.
  
  - 04 / 25 2021
    - Handle url reset error.
  
  - 04 / 22 2021
    - Handle http 404 not found error.
  
  - 04 / 15 2021
    - Restrict max length of filename.
  
  - 04 / 05 2021
    - Add changelog section in README.md .
    - Add specification section in README.md .
    - Modify playlist download code in main.py .
    - Add progress bar in downloadFile() and playlistToTs() in main.py .

</details>

# TODO or Known Issues

- Refactor code using **OOP principles**.
- Optimize the **self-test function**.
- Integrate **mypy** or **pyright** for syntax checking.
- Fix bugs for **tktube** and **iwant**.
- Remove unnecessary suffixes from website titles.
- Add **multi-threaded support** for faster downloads.

# Copyright

This program is written by [haward79](https://www.haward79.tw/).

This is a **COPYLEFT program**!
Everyone can edit and share this program for free (without payment) as long as the original author is credited.

> Any program developed based on this software must also comply with the copyleft policy.

> [!NOTE]
> The author is **not responsible** for the videos downloaded using this program.  
> Please use the program responsibly and legally.
