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
uv run python main.py -h
```

Then, follow the on-screen instructions to start using the program.

# TODO or Known Issues

- Optimize the **self-test function**.
- Fix bugs for **tktube** and **iwant**.
- Add **multi-threaded support** for faster downloads.

# Copyright

This program is written by [haward79](https://www.haward79.tw/).

This is a **COPYLEFT program**!
Everyone can edit and share this program for free (without payment) as long as the original author is credited.

> Any program developed based on this software must also comply with the copyleft policy.

> [!NOTE]
> The author is **not responsible** for the videos downloaded using this program.  
> Please use the program responsibly and legally.
