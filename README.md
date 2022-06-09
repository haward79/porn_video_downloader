# What's this
This is a online video downloader.

This program supports videos on the following websites :
- xvideos.com
- porn5f.com
- 85tube.com
- tktube.com

# Specification
- Urls are able to read from file or keyboard.
- Customize download directory.
- Automatically name videos by web titles.
- Automatically resolve naming conflict.
- Download videos serially.
- Progress bar for download and processing.

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

To run the program, Please open terminal and run the following commands.

    python3 main.py

Then, follow the instructions to choose a created directory for saving downloaded videos.

Finally, input the video urls from file or keyboard.

# Changelog
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
All rights reserved by haward79.

Everyone can spread the program with name-tagged.
However, editing is NOT allowed.

**The videos downloaded by this program is not responsible by the author of program.  
Please use this program with care.**

