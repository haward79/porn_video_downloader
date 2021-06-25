
""" Import """
from os import system
from os import stat
from os import remove
from os import path
from os import popen
from urllib import request
from urllib import error
import requests
from math import ceil

""" Define constant """
kMaxFilenameLength = 95


def getTerminalSize():

    (rows, cols) = popen('stty size').read().split()
    rows = int(rows)
    cols = int(cols)

    return {'row': rows, 'col': cols}


def fetchString(str, startIndex, endDelimiter):

    endIndex = str.find(endDelimiter, startIndex+1)

    return str[startIndex:endIndex]


def retrieveSourceCode(url):

    req = request.Request(url)
    req.add_header(
        'User-Agent', 'Mozilla/5.0 (X11; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0')

    try:
        sourceCode = request.urlopen(req).read().decode('utf-8')
    except error.HTTPError:
        return ''

    return sourceCode


def get_85tube_videoUrl(url):

    sourceCode = retrieveSourceCode(url)
    pos = sourceCode.find('video_url')

    if pos != -1:
        videoUrl = fetchString(sourceCode, pos + 12, "'")
    else:
        videoUrl = ''

    return videoUrl


def get_porn5f_videoUrl(url):

    sourceCode = retrieveSourceCode(url)
    pos = sourceCode.find('source src="')

    if pos != -1:
        videoUrl = fetchString(sourceCode, pos + 12, '"')
    else:
        videoUrl = ''

    return videoUrl


def get_xvideos_videoUrl(url):

    sourceCode = retrieveSourceCode(url)
    pos = sourceCode.find('html5player.setVideoUrlHigh')

    if pos != -1:
        videoUrl = fetchString(sourceCode, pos + 29, "'")
    else:
        videoUrl = ''

    return videoUrl


def formatFilename(filename):

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


def getWebsiteTitle(url):

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


def getUniqueFilename(directory, name, extName):

    if len(directory + name) > kMaxFilenameLength:
        name = name[0: (kMaxFilenameLength-len(directory))]

    index = 0
    baseName = name

    while path.isfile(directory + name + extName):
        index += 1
        name = baseName + " (" + str(index) + ")"

    return name


def getReadableSize(byteSize):

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


def downloadFile(url, filename, showProgress):

    kHeaders = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0'}

    if showProgress:
        print('Download file ......')

    # Ignore blank url or blank filename.
    if url == '' or filename == '':
        return False

    else:
        # Download file.
        req = requests.get(url, stream=True, headers=kHeaders)
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


def playlistToMp4(input, output):

    system("ffmpeg -loglevel quiet -protocol_whitelist file,crypto,data,http,https,tls,tcp -i '{}' '{}' ".format(input, output))

    # File exists.
    if path.isfile(output):

        # File size not empty.
        if stat(output).st_size > 0:
            return True
        else:
            remove(output)
            return False

    else:
        return False


def playlistToTs(input, output, showProgress):

    urls = []

    print('Download video trims from playlist ......')

    # Read urls in playlist.
    with open(input, "r") as fin:
        lines = fin.readlines()

        for i in lines:
            if i.startswith("http"):
                urls.append(i)

    data = bytearray(b'')

    # Download and concat video trims.
    countUrls = len(urls)

    for i in range(countUrls):
        url = urls[i]
        req = request.Request(url)
        req.add_header(
            'User-Agent', 'Mozilla/5.0 (X11; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0')

        try:
            resp = request.urlopen(req).read()
        except error.URLError:
            return False

        data += resp

        if showProgress:
            cols = getTerminalSize()['col'] - 10
            progress = (i + 1) / countUrls
            progress100 = int(progress * 100)
            countDone = int(cols * progress)
            countUndone = cols - countDone
            print('\r[%s%s] %3d%%' %
                  ('=' * countDone, ' ' * countUndone, progress100), end='')

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


""" Main """

print('+------------------------------+')
print('|                              |')
print('|  ' + BashColor.kRed + 'Porn Video Downloader' +
      BashColor.kClear + '       |')
print('|                              |')
print('+------------------------------+')
print('|  ' + BashColor.kGreen + 'Supported Sites :' +
      BashColor.kClear + '           |')
print('|    https://85tube.com/       |')
print('|    https://porn5f.com/       |')
print('|    https://xvideos.com/      |')
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
        if downloadFile(videoUrl, downloadDirectory + videoTitle + extName, withProgress):
            # Deal with playlist.
            if extName == ".m3u8":
                # Get unique filename.
                videoTitleTs = getUniqueFilename(
                    downloadDirectory, videoTitle, ".ts")

                # Download videos in playlist.
                if playlistToTs(downloadDirectory + videoTitle + extName, downloadDirectory + videoTitleTs + ".ts", True):
                    print("Download '{}' successfully.".format(
                        videoTitleTs + ".ts"))
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
    with open("failed.txt", "w") as fout:
        for i in failedUrl:
            fout.write(i + "\n")

    print("All url(s) which downloaded failed are output to failed.txt .")

print()
