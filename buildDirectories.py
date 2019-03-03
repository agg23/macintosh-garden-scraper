import os, shutil, errno

from entry import loadEntries

APPS_DIR = 'Macintosh_Garden_Apps_Collection_'
GAMES_DIR = 'Macintosh_Garden_Games_Collection_'
OS_DIR = 'Macintosh_Garden_OS_Collection'

def makeDirectory(directory):
    try:
        os.makedirs(directory)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

def findExistingDownload(archiveRoot, downloadName):
    firstChar = downloadName[0].upper()

    if firstChar.isnumeric():
        appDir = archiveRoot + APPS_DIR + '0/' + downloadName
        if os.path.isfile(appDir):
            return appDir

    appDir = archiveRoot + APPS_DIR + firstChar + '/' + downloadName
    if os.path.isfile(appDir):
        return appDir

    gameDir = archiveRoot + GAMES_DIR + firstChar + '/' + downloadName
    if os.path.isfile(gameDir):
        return gameDir

    osDir = archiveRoot + OS_DIR + '/' + downloadName
    if os.path.isfile(osDir):
        return osDir

    return None

def saveDownload(archiveRoot, download, directory, filename):
    existingFile = findExistingDownload(archiveRoot, download.name)

    if not existingFile:
        return

    makeDirectory(directory)

    shutil.copyfile(existingFile, directory + '/' + filename)

def main():
    outputRoot = 'Y:/Downloads/Processed/'
    archiveRoot = 'Y:/Downloads/complete/'

    groupedEntries = loadEntries('groupedEntries.json')
    entryPathToDownloads = loadEntries('entryPathToDownloads.json')

    limit = 100
    count = 0

    for entryKey in groupedEntries:
        if count > limit:
            break
        for entry in groupedEntries[entryKey]:
            if entry.source not in entryPathToDownloads:
                print 'No downloads for ' + entry.title
                break

            downloadGroupList = entryPathToDownloads[entry.source]

            for downloadGroup in downloadGroupList:
                saveDownload(archiveRoot, downloadGroup['download'], outputRoot + downloadGroup['directory'], downloadGroup['filename'])

        count += 1

if __name__ == '__main__':
    main()
