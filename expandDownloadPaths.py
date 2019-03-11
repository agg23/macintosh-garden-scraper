import os

from entry import loadEntries
from util import save
from decompress import getFileList
from buildDirectories import findExistingDownload

def extractRootFolderNames(paths):
    rootFolders = [next(part for part in path.split('/') if part) for path in paths if path != '']

    return list(set(rootFolders))

def main():
    archiveRoot = 'Y:/Downloads/complete/'
    useFilename = False

    entryPathToDownloads = loadEntries('entryPathToDownloads.json')

    outputPaths = []
    
    for key in entryPathToDownloads:
        downloadList = entryPathToDownloads[key]

        for download in downloadList:
            outputPath = ''

            if useFilename:
                outputPath = download['filename']
            else:
                entryDownload = download['download']
                existingPath = findExistingDownload(archiveRoot, entryDownload.name)

                if not existingPath:
                    continue
                
                fileList = getFileList(existingPath)
                rootFolders = extractRootFolderNames(fileList)

                if len(rootFolders) != 1:
                    print 'Invalid number of root folders'
                    print rootFolders
                    continue
                
                outputPath = rootFolders[0]

            outputPaths.append(download['directory'] + outputPath)

    outputPaths.sort()

    save(outputPaths, 'outputPaths.json')


if __name__ == '__main__':
    main()