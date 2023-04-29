# What's this
This is an online video downloader.

This program supports videos on the following websites:
- xvideos.com
- porn5f.com
- 85tube.com
- tktube.com
- missav.com

# Specification
- File or keyboard input are both supported for video urls.
- Users can select download directory by themselves.
- This program can retrieve web page titles as video filenames automatically.
- Videos are downloaded serially with retry on failure mechanism.
- Progress bars are available during download.
- Silent mode with no extra output is supported.
- This program is written with detailed log mechanism for easy debugging.

# Pre-requirements
- Software
  - Linux based OS
    - *Note : This program may run on Windows by modifying some codes.*
  - Python 3
  - Python 3 Library - Selenium (web browser driver)
    - Please install appropriate web browser and driver for selenium(python library).
    - You can get reference from [selenium website](https://pypi.org/project/selenium/).
  - Web Browser (with media codecs)
    - You can install the codecs by apt with package name libavcodec-extra.

# Install
This program doesn't need to install.

# Usage
To get help, please open terminal and run the following command.
```
    python3 main.py -h
```

Then, follow the instructions to enjoy this program.

# Changelog
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

# Copyright
This program is written by [haward79](https://www.haward79.tw/).

This is a COPYLEFT program!
Everyone can edit and share this program to others for free(without payment and with freedom) with name-tagged.

Please note: Any program developed based on this program needs to follow the copyleft policy!

**The videos downloaded by this program is not responsible by the author of program.  
Please use this program with care.**
