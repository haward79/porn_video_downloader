
""" Import """
from os import stat
from os import remove
from os import path
from os import popen
from math import ceil
from time import sleep
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import argparse

""" Define constant """
kRequestsHeaders = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0'}
kMaxFilenameLength = 95


def getTerminalSize() -> dict:

    rows = 0
    cols = 0

    try:
        (rows, cols) = popen('stty size').read().split()
    except:
        print('Failed to get size of terminal.')
    else:
        rows = int(rows)
        cols = int(cols)

    return {'row': rows, 'col': cols}


def fetchString(str: str, startIndex: int, endDelimiter: str) -> str:

    endIndex = str.find(endDelimiter, startIndex+1)

    return str[startIndex:endIndex]


def retrieveSourceCode(url: str) -> str:

    global kRequestsHeaders

    response = requests.get(url, headers=kRequestsHeaders, verify=False)
    sourceCode = response.content.decode('utf-8')

    return sourceCode


def retrieveSourceCodeWithJs(url: str) -> str:

    firefoxOptions = webdriver.FirefoxOptions()
    firefoxOptions.add_argument('-headless')

    firefox = webdriver.Firefox(options=firefoxOptions)
    firefox.get(url)
    sourceCode = firefox.page_source

    firefox.close()

    if path.isfile('geckodriver.log'):
        remove('geckodriver.log')

    return sourceCode


def get_85tube_videoUrl(url: str) -> str:

    videoUrl = ''

    firefoxOptions = webdriver.FirefoxOptions()
    firefoxOptions.add_argument('-headless')

    firefox = webdriver.Firefox(options=firefoxOptions)
    
    for i in range(5):
        firefox.get(url)
        
        try:
            video = firefox.find_element(By.CSS_SELECTOR, '#kt_player video')
        except:
            print('Failed to locate video element')
            sleep(0.5)
        else:
            print('Video element located successfully')
            videoUrl = video.get_attribute('src')
            break

    firefox.close()

    if path.isfile('geckodriver.log'):
        remove('geckodriver.log')
    
    return videoUrl


def get_porn5f_videoUrl(url: str) -> str:

    sourceCode = retrieveSourceCode(url)
    pos = sourceCode.find('source src="')

    if pos != -1:
        videoUrl = fetchString(sourceCode, pos + 12, '"')
    else:
        videoUrl = ''

    return videoUrl


def get_xvideos_videoUrl(url: str) -> str:

    sourceCode = retrieveSourceCode(url)
    pos = sourceCode.find('html5player.setVideoHLS')

    if pos != -1:
        videoUrl = fetchString(sourceCode, pos+25, "'")
    else:
        videoUrl = ''

    return videoUrl


def get_tktube_videoUrl(url: str) -> str:

    videoUrl = ''

    firefoxOptions = webdriver.FirefoxOptions()
    firefoxOptions.add_argument('-headless')

    firefox = webdriver.Firefox(options=firefoxOptions)
    firefox.get(url)

    try:
        showVideoButton = firefox.find_element(By.CSS_SELECTOR, '.fp-ui')
    except:
        firefox.close()

        if path.isfile('geckodriver.log'):
            remove('geckodriver.log')

        return ''
    
    firefox.execute_script("arguments[0].click();", showVideoButton)
    
    try:
        WebDriverWait(firefox, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'video[src*=\'tktube.com/get_file/\']')))
    except:
        firefox.close()

        if path.isfile('geckodriver.log'):
            remove('geckodriver.log')

        return ''
    
    video = firefox.find_element(By.CSS_SELECTOR, 'video[src*=\'tktube.com/get_file/\']')
    videoUrl = video.get_attribute('src')

    firefox.close()

    if path.isfile('geckodriver.log'):
        remove('geckodriver.log')
    
    return videoUrl


def formatFilename(filename: str) -> str:

    # Remove html entities.
    while True:
        pos1 = filename.find("&")
        pos2 = filename.find(";")

        if pos1 != -1 and pos2 != -1 and pos2 - pos1 <= 10:
            filename = filename.replace(filename[pos1:pos2+1], "")
        else:
            break

    # Remove line endings.
    filename = filename.replace("\n", "")
    filename = filename.replace("\r", "")

    # Replace half characters to full characters.
    filename = filename.replace("(", "（")
    filename = filename.replace(")", "）")
    filename = filename.replace("[", "「")
    filename = filename.replace("]", "」")
    filename = filename.replace("<", "「")
    filename = filename.replace(">", "」")
    filename = filename.replace("{", "「")
    filename = filename.replace("}", "」")
    filename = filename.replace("*", "＊")
    filename = filename.replace("+", "＋")
    filename = filename.replace("=", "＝")
    filename = filename.replace(":", "：")
    filename = filename.replace(";", "；")

    # Replace special characters.
    filename = filename.replace("&", "_")
    filename = filename.replace("!", "_")
    filename = filename.replace("?", "_")
    filename = filename.replace("#", "_")
    filename = filename.replace("$", "_")
    filename = filename.replace("%", "_")
    filename = filename.replace("^", "_")
    filename = filename.replace("|", "_")
    filename = filename.replace("/", "_")

    # Remove special characters.
    filename = filename.replace(",", "")
    filename = filename.replace(".", "")

    # Replace continuous spaces to one space.
    while filename.find("  ") != -1:
        filename = filename.replace("  ", " ")

    # Replace continuous underline to one space.
    while filename.find("__") != -1:
        filename = filename.replace("__", "_")

    return filename


def getWebsiteTitle(url: str) -> str:

    sourceCode = retrieveSourceCode(url)
    startIndex = sourceCode.find("<title>")

    if startIndex == -1:
        return ""
    else:
        startIndex += 7
        endingIndex = sourceCode.find("</title>", startIndex)

        if endingIndex == -1:
            return ""
        else:
            return sourceCode[startIndex:endingIndex]


def getUniqueFilename(directory: str, name: str, extName: str) -> str:

    if len(directory + name) > kMaxFilenameLength:
        name = name[0: (kMaxFilenameLength-len(directory))]

    index = 0
    baseName = name

    while path.isfile(directory + name + extName):
        index += 1
        name = baseName + " (" + str(index) + ")"

    return name


def getReadableSize(byteSize: int) -> str:

    kSizeName = ('B', 'KB', 'MB', 'GB', 'TB')
    level = 0
    byteSize = float(byteSize)

    while byteSize > 1024:
        byteSize /= 1024
        level += 1

        if level >= len(kSizeName) - 1:
            break

    byteSize = ceil(byteSize * 100) / 100

    return (str(byteSize) + ' ' + kSizeName[level])


def downloadFile(url: str, filename: str, showProgress: bool) -> bool:

    global kRequestsHeaders

    if showProgress:
        print('Download file ......')

    # Ignore blank url or blank filename.
    if url == '' or filename == '':
        return False

    else:
        # Download file.
        req = requests.get(url, stream=True, headers=kRequestsHeaders, verify=False)
        contentBytes = req.headers.get('content-length')
        dlBytes = 0
        sliceBytes = 4096

        # Output file to local disk.
        with open(filename, "wb") as fout:

            if showProgress:
                if contentBytes == None:
                    print('Warning: file size is unavailable.')
                    fout.write(req.content)

                else:
                    contentBytes = int(contentBytes)
                    print('File size : {}'.format(
                        getReadableSize(contentBytes)))

                    # Write data 4KB at once.
                    for sliceData in req.iter_content(chunk_size=sliceBytes):

                        # Write to disk.
                        fout.write(sliceData)

                        # Print progress bar.
                        cols = getTerminalSize()['col'] - 10
                        dlBytes += sliceBytes
                        progress = dlBytes / contentBytes
                        progress100 = int(progress * 100)
                        countDl = int(cols * progress)
                        countNdl = cols - countDl
                        print('\r[%s%s] %3d%%' % ('=' * countDl,
                                                  ' ' * countNdl, progress100), end='')

                    print()

            else:
                fout.write(req.content)

        # Check download file existence.
        if path.isfile(filename):
            # Check download file size.
            if stat(filename).st_size > 0:
                return True

            # Remove empty file.
            else:
                remove(filename)
                return False
        # File doesn't exist.
        else:
            return False


def playlistToTs(input: str, originalUrl: str, output: str, showProgress: bool) -> bool:

    global kRequestsHeaders
    urls = []
    resolutions = []
    resolutions_url = {}

    print('Download video trims from playlist ......')

    # Read urls in playlist.
    with open(input, "r") as fin:
        lines = fin.readlines()

        for i in lines:
            i = i.replace('\n', '')

            if i.startswith("http"):
                urls.append(i)
            elif i.startswith('hls-'):
                resolution = int(fetchString(i, 4, 'p'))
                resolutions.append(resolution)
                resolutions_url[str(resolution)] = i

    if len(urls) == 0 and len(resolutions) > 0:
        resolutions.sort(reverse=True)
        resolution = resolutions[0]
        filename = resolutions_url[str(resolution)]

        print('The best resolution is {}p.'.format(resolution))

        pos = originalUrl.rfind('/')
        if pos != -1:
            baseUrl = originalUrl[0:pos] + '/'
            playlist_url = baseUrl + filename

            if downloadFile(playlist_url, input, showProgress):
                with open(input, "r") as fin:
                    lines = fin.readlines()

                    for i in lines:
                        if not i.startswith('#'):
                            filename = i.replace('\n', '')
                            urls.append(baseUrl + filename)

    # Download and concat video trims.
    countUrls = len(urls)
    data = bytearray(b'')

    for i in range(countUrls):
        url = urls[i]

        response = requests.get(url, headers=kRequestsHeaders, verify=False)
        data += response.content

        if showProgress:
            cols = getTerminalSize()['col'] - 10
            progress = (i + 1) / countUrls
            progress100 = int(progress * 100)
            countDone = int(cols * progress)
            countUndone = cols - countDone
            print('\r[%s%s] %3d%%' % ('=' * countDone, ' ' * countUndone, progress100), end='')

    if showProgress:
        print()

    # Output video to local disk.
    with open(output, "wb") as fout:
        fout.write(data)

    # Check video file existence.
    if path.isfile(output):

        # Video file not empty.
        if stat(output).st_size > 0:
            return True
        else:
            remove(output)
            return False

    else:
        return False


class BashColor:

    # Constant.
    kClear = '\033[0m'
    kRed = '\033[91m'
    kGreen = '\033[92m'


def interactiveMenu():

    print('+------------------------------+')
    print('|                              |')
    print('|  ' + BashColor.kRed + 'Porn Video Downloader' + BashColor.kClear + '       |')
    print('|                              |')
    print('+------------------------------+')
    print('|  ' + BashColor.kGreen + 'Supported Sites :' + BashColor.kClear + '           |')
    print('|    https://85tube.com/       |')
    print('|    https://porn5f.com/       |')
    print('|    https://xvideos.com/      |')
    print('|    https://tktube.com/       |')
    print('+------------------------------+')

    while True:
        downloadDirectory = input('\nPlease input download directory : ')

        # Set default directory to current workspace.
        if downloadDirectory == '':
            downloadDirectory = './'
            break

        # Set directory to exists directory.
        elif path.exists(downloadDirectory):
            if not downloadDirectory.endswith('/'):
                downloadDirectory = downloadDirectory + "/"

            break

        # Directory doesn't exist.
        else:
            print("Invalid directory path : {}".format(downloadDirectory))

    # Print target directory.
    print("Download directory is set to '{}' .\n".format(downloadDirectory))


    """ Read urls """

    urls = []

    isFromFile = input("Do you want to read url(s) from file ? [y/N] ")

    if isFromFile == "y" or isFromFile == "Y":
        # Input filename.
        while True:
            filepath = input('Please input full file path : ')

            if path.isfile(filepath):
                break
            else:
                print("Invalid file path '{}' .\n".format(filepath))

        print("Read url(s) from '{}' .".format(filepath))

        # Read file contains urls.
        with open(filepath, "r") as fin:
            urls = fin.readlines()

        # Deal urls.
        i = 0
        length = len(urls)
        while i < length:
            # Remove line endings.
            urls[i] = urls[i].replace("\r", "")
            urls[i] = urls[i].replace("\n", "")

            # Remove empty urls.
            if urls[i] == "":
                urls.remove(urls[i])
                length -= 1
            else:
                i += 1

        print("Total reads {} line(s).".format(len(urls)))

    else:
        url = input("Please input website url : ")
        urls.append(url)

    return (downloadDirectory, urls)


""" Main """

if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description='Download porn videos. To use interactive mode, please run without argument. To use silent mode, please run with all following arguments')
    argparser.add_argument('--urls-file', dest = 'file_path', help = 'Filename or filepath which contains url to be downloaded')
    argparser.add_argument('--target-dir', dest = 'download_directory', help = 'Target directory to save downloaded videos')
    argparser.add_argument('--work-dir', dest = 'work_dir', help = 'Working directory to output failed.txt')
    args = argparser.parse_args()

    isSilentMode = False

    if args.file_path == None and args.download_directory == None:
        (downloadDirectory, urls) = interactiveMenu()

    elif args.file_path != None and args.download_directory != None:
        isSilentMode = True
        
        downloadDirectory = args.download_directory
        filepath = args.file_path
        workDirectory = args.work_dir

        if not path.exists(downloadDirectory):
            print(BashColor.kRed + 'Invalid directory to save videos !\n' + BashColor.kClear)
            exit()
        
        else:
            if not downloadDirectory.endswith('/'):
                downloadDirectory = downloadDirectory + "/"

            print("Download directory is set to {} .\n".format(downloadDirectory))

        if not path.exists(filepath):
            print(BashColor.kRed + 'Invalid file path for urls !\n' + BashColor.kClear)
            exit()

        else:
            with open(filepath, 'r') as fin:
                urls = fin.readlines()

            # Deal urls.
            i = 0
            length = len(urls)
            while i < length:
                # Remove line endings.
                urls[i] = urls[i].replace("\r", "")
                urls[i] = urls[i].replace("\n", "")

                # Remove empty urls.
                if urls[i] == "":
                    urls.remove(urls[i])
                    length -= 1
                else:
                    i += 1

            print("Total reads {} url(s).".format(len(urls)))

        if not path.exists(workDirectory):
            print(BashColor.kRed + 'Invalid work directory !\n' + BashColor.kClear)
            exit()
        
        else:
            if not workDirectory.endswith('/'):
                workDirectory = workDirectory + "/"

            print("Work directory is set to {} .\n".format(workDirectory))

    else:
        argparser.print_help()
        exit()

    # Setup for downloading.
    countTotal = len(urls)
    countFailed = 0
    failedUrl = []

    # Download each urls.
    for i in range(len(urls)):
        url = urls[i]
        checkFlag = True

        # Print case number.
        print(("\n" + BashColor.kGreen +
            "[ Case {} ]" + BashColor.kClear).format(i+1))

        # 85tube.com
        if url.find('85tube.com') != -1:
            videoUrl = get_85tube_videoUrl(url)
            extName = ".mp4"
            withProgress = True

        # porn5f.com
        elif url.find('www.porn5f.com') != -1:
            videoUrl = get_porn5f_videoUrl(url)
            extName = ".m3u8"
            withProgress = False

        # xvideos.com
        elif url.find('www.xvideos.com') != -1:
            videoUrl = get_xvideos_videoUrl(url)
            extName = ".m3u8"
            withProgress = True

        # tktube.com
        elif url.find('tktube.com') != -1:
            videoUrl = get_tktube_videoUrl(url)
            extName = ".mp4"
            withProgress = True

        # Not support website.
        else:
            checkFlag = False

        # Check domain of target website.
        if checkFlag:
            # Get web page title as video title.
            videoTitle = formatFilename(getWebsiteTitle(url))

            # Get unique filename.
            videoTitle = getUniqueFilename(downloadDirectory, videoTitle, extName)

            # Download video.
            if videoUrl == '':
                print(BashColor.kRed + 'Failed to fetch video url !' + BashColor.kClear)
                failedUrl.append(url)
                countFailed += 1

            elif downloadFile(videoUrl, downloadDirectory + videoTitle + extName, (not isSilentMode) and withProgress):
                # Deal with playlist.
                if extName == ".m3u8":
                    # Get unique filename.
                    videoTitleTs = getUniqueFilename(downloadDirectory, videoTitle, ".ts")

                    # Download videos in playlist.
                    if playlistToTs(downloadDirectory + videoTitle + extName, videoUrl, downloadDirectory + videoTitleTs + ".ts", not isSilentMode):
                        print("Download '{}' successfully.".format(videoTitleTs + ".ts"))
                    else:
                        print("Download '{}' failed.".format(videoTitleTs + ".ts"))
                        failedUrl.append(url)
                        countFailed += 1

                    # Remove playlist file.
                    remove(downloadDirectory + videoTitle + extName)

                else:
                    print("Download '{}' successfully.".format(videoTitle + extName))

            else:
                print("Download '{}' failed.".format(videoTitle + extName))
                failedUrl.append(url)
                countFailed += 1

        else:
            print('Unsupported website #{}#.'.format(url))

    # Print summary.
    print("\n==== Complete =======================")
    print("  Total {} , Success {} , Failed {}".format(
        countTotal, (countTotal-countFailed), countFailed))

    # Output failed to file.
    if countFailed > 0:
        with open(workDirectory + "failed.txt", "w") as fout:
            for i in failedUrl:
                fout.write(i + "\n")

        print('All url(s) which downloaded failed are output to "{}failed.txt" .'.format(workDirectory))

    print()

