import collections
import copy
import re

from entry import Entry, Application, Rating, jsonDecode, loadEntries
from filter import (extractArchitecture, extractVersionNumber, stripBetweenParens, stripFirstHyphen, stripFirstWords, 
    stripSpacing, stripStringsFromStringIfNeeded, stripStrippableWords)
from util import firstOrNone, isYear, save, stripMultipleSpaces, stripStringFromString

MAC_SYSTEM_NUMBER = re.compile(r'(system|mac\s?os)\s?([0-9.x]+)', re.IGNORECASE)
OS_NUMBER = re.compile(r'\b([0-9.X]+)\b')
MAJOR_VERSION = re.compile(r'([0-9]+)[._-]')

INVALID_PATH_CHARS_MAP = {ord(c): ord('-') for c in '/:'}

EXTENSION_MAP = {'image': 'img'}

def osVersionRange(osVersion):
    if osVersion is None:
        return None

    matches = OS_NUMBER.findall(osVersion)

    if len(matches) < 1:
        return None

    firstOsString = matches[0]
    lastOsString = matches[-1]

    if firstOsString.lower() == 'x':
        firstOsString = '10'

    if lastOsString.lower() == 'x':
        lastOsString = '10'
    
    firstOs = float(firstOsString)
    lastOs = float(lastOsString)

    minOs = min(firstOs, lastOs)
    maxOs = max(firstOs, lastOs)

    return (minOs, maxOs)

"""
For now, simply returns the path of the "created" directory
"""
def buildDirectory(entry):
    publisher = firstOrNone(entry.publisher)

    if publisher is None:
        publisher = firstOrNone(entry.author)

    if publisher is None:
        publisher = u'Unknown'
        
    originalPublisher = publisher

    publisher = publisher.translate(INVALID_PATH_CHARS_MAP)

    # Attempt to strip between parens
    publisher = stripBetweenParens(publisher)

    publisher = stripStrippableWords(publisher)

    if len(publisher) > 31:
        print 'Publisher ' + publisher + ' is too long (original "' + originalPublisher + '")'

    productName = entry.title
    productName = productName.translate(INVALID_PATH_CHARS_MAP)

    # Attempt to strip between parens
    productName = stripBetweenParens(productName)

    # Attempt to strip publisher/author name
    productName = stripStringsFromStringIfNeeded(entry.author, productName)
    productName = stripStringsFromStringIfNeeded(entry.publisher, productName)

    productName = stripStrippableWords(productName)

    if len(productName) > 31:
        print 'Product "' + productName + '" is too long (original title "' + entry.title + '")'

    majorVersion = ''
    if hasattr(entry, 'versionRange'):
        majorVersion = entry.version
    elif hasattr(entry, 'version'):
        majorVersionMatch = MAJOR_VERSION.search(entry.version)
        majorVersion = entry.version + '/'

        if majorVersionMatch:
            majorVersion = majorVersionMatch.group(1) + '/'

    return ('/' + publisher + '/' + productName + '/' + majorVersion).encode('ascii', 'ignore')

def suggestFileName(entry, download):
    fileName = ''
    existingFullFileName = download.name

    versionNumber = ''

    if hasattr(entry, 'version'):
        versionNumber = entry.version

    versionNumberMatch = extractVersionNumber(existingFullFileName, True)

    if versionNumberMatch[0] is not None:
        versionNumber = versionNumberMatch[0]
        existingFullFileName = versionNumberMatch[1]

    splitName = existingFullFileName.split('.')

    if len(splitName) < 2:
        print 'No file extension'
        return None

    extensions = []
    # Process extension
    for extension in splitName[1:]:
        newExtension = extension.replace('_', '').lower()

        if newExtension in EXTENSION_MAP:
            newExtension = EXTENSION_MAP[newExtension]

        extensions.append(newExtension)

    # Wipe underscores from extension
    extension = '.'.join(extensions)

    if versionNumber != '':
        versionNumber = ' ' + versionNumber

    newTitle = entry.title
    fileArchitecture = extractArchitecture(download.name)

    if fileArchitecture:
        newTitle += ' ' + fileArchitecture

    strippedTitle = newTitle.replace(':', ' - ')

    fileName = stripMultipleSpaces(strippedTitle + versionNumber + '.' + extension)

    if len(fileName) > 31:
        # Attempt to strip publisher/author name
        fileName = stripStringsFromStringIfNeeded(entry.author, fileName)
        fileName = stripStringsFromStringIfNeeded(entry.publisher, fileName)

        # Attempt to strip between parens
        fileName = stripBetweenParens(fileName)

        # Attempt to strip before divider "-"
        fileName = stripFirstHyphen(fileName)

        # Attempt to strip unneeded words
        fileName = stripStrippableWords(fileName)

        spacedShrunkFileName = fileName

        fileName = stripSpacing(fileName)

        # Stripping spacing wasn't enough, start dropping words
        fileName = stripFirstWords(fileName, spacedShrunkFileName)

        if len(fileName) <= 31:
            # print 'Successfully shrunk ' + fileName
            pass
        else:
            print 'Failed to shrink ' + fileName

    return fileName.encode('ascii', 'ignore')

def main():
    entries = []

    for year in range(1984, 1990):
        entries.extend(loadEntries('data/' + str(year) + '.json'))

    newEntries = []
    entryPathToDownloads = {}

    for entry in entries:
        newEntry = copy.copy(entry)

        title = entry.title
        # newTitle = title

        versionNumberMatch = extractVersionNumber(title, False)

        if versionNumberMatch[2]:
            # Version range
            newEntry.versionRange = True

        if versionNumberMatch[0] is not None:
            newEntry.version = versionNumberMatch[0]
            newEntry.title = versionNumberMatch[1]

        directory = buildDirectory(newEntry)

        if hasattr(entry, 'downloads'):
            downloads = []
            for download in entry.downloads:
                fileName = suggestFileName(newEntry, download)
                osVersions = osVersionRange(download.version)

                if osVersions is not None:
                    download.minOs = osVersions[0]
                    download.maxOs = osVersions[1]
                
                downloads.append({
                    'directory': directory,
                    'filename': fileName,
                    'download': download,
                })

            entryPathToDownloads[entry.source] = downloads

        newEntries.append(newEntry)

    groupedEntries = {}

    for entry in newEntries:
        if entry.title in groupedEntries:
            currentEntries = groupedEntries[entry.title]
            currentEntries.append(entry)
        else:
            groupedEntries[entry.title] = [entry]

    orderedgroupedEntries = collections.OrderedDict(sorted(groupedEntries.iteritems()))
    save(orderedgroupedEntries, 'groupedEntries.json')
    save(entryPathToDownloads, 'entryPathToDownloads.json')

    # save(newEntries, '1984-1989modified.json')
    # save(downloads, '1984-1989downloads.json')

if __name__ == '__main__':
    main()
