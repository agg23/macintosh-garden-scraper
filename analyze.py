import copy
import json
import re

from entry import Entry, Application, Rating
from util import firstOrNone, save, stripMultipleSpaces, stripStringFromString

EXTENSION_END_OF_STRING_VERSION_NUMBER = r'(\.[a-z]*)*$'
VERSION_NUMBER_MAIN = r'(([0-9]|\.(?=[0-9])|v(?=[0-9]))([0-9]|[._](?=[0-9]|x(?=\b|\s)))*([a-z](?=[0-9.]|\b))?)'

VERSION_NUMBER = re.compile(VERSION_NUMBER_MAIN, re.IGNORECASE)
VERSION_NUMBER_END_OF_STRING = re.compile(VERSION_NUMBER_MAIN + EXTENSION_END_OF_STRING_VERSION_NUMBER, re.IGNORECASE)
MAC_SYSTEM_NUMBER = re.compile(r'(system|mac\s?os)\s?([0-9.x]+)', re.IGNORECASE)
OS_NUMBER = re.compile(r'\b([0-9.X]+)\b')

STRIP_PARENS = re.compile(r'(\([a-z0-9./ -]*\))', re.IGNORECASE)

EXTENSION_MAP = {'image': 'img'}

ENTRY_KEYS = ['source', 'title', 'type']
APPLICATION_KEYS = ['name', 'size', 'version']
RATING_KEYS = ['average', 'count']

STRIPPABLE_WORDS = ['macintosh', 'the', 'of', 'in', 'an', 'a']

def jsonDecode(dictionary):
    if hasKeys(dictionary, ENTRY_KEYS):
        entry = Entry(dictionary.get('source'), dictionary.get('title'), dictionary.get('type'), dictionary.get('category'),
            dictionary.get('year'), dictionary.get('author'), dictionary.get('publisher'), dictionary.get('description'), dictionary.get('architecture'))

        rating = dictionary.get('rating')
        if rating is not None:
            entry.rating = rating

        entry.compatibilityText = dictionary.get('compatibilityText')

        downloads = dictionary.get('downloads')
        if downloads is not None:
            entry.downloads = downloads
        
        manuals = dictionary.get('manuals')
        if manuals is not None:
            entry.manuals = manuals

        return entry
    elif hasKeys(dictionary, APPLICATION_KEYS):
        return Application(dictionary.get('name'), dictionary.get('size'), dictionary.get('version'))
    elif hasKeys(dictionary, RATING_KEYS):
        return Rating(dictionary.get('average'), dictionary.get('count'))
    
    return dictionary

def hasKeys(dictionary, keys):
    for key in keys:
        if key not in dictionary:
            return False

    return True

def loadEntries(name):
    with open(name, 'r') as infile:
        return json.load(infile, object_hook=jsonDecode)

def osVersionRange(osVersion):
    if osVersion is None:
        return None

    matches = OS_NUMBER.findall(osVersion)

    if len(matches) < 1:
        return None
    
    firstOs = float(matches[0])
    lastOs = float(matches[-1])

    minOs = min(firstOs, lastOs)
    maxOs = max(firstOs, lastOs)

    return (minOs, maxOs)

def isYear(value):
    return value.isdigit() and len(value) == 4

"""
For now, simply returns the path of the "created" directory
"""
def buildDirectory(entry):
    author = firstOrNone(entry.author)

    if author is None:
        author = firstOrNone(entry.publisher)

    if author is None:
        author = 'Unknown'

    productName = entry.title

    return '/' + author + '/' + productName + '/'

def suggestFileName(entry, download):
    fileName = ''
    existingFullFileName = download.name

    versionNumberMatch = VERSION_NUMBER_END_OF_STRING.search(existingFullFileName)
    versionNumber = ''

    if hasattr(entry, 'version'):
        versionNumber = entry.version

    if versionNumberMatch:
        versionNumberString = versionNumberMatch.group(1)
        if not isYear(versionNumberString):
            # Any underscores should be periods instead
            versionNumber = versionNumberString.replace('_', '.')
            # Strip version number from filename
            existingFullFileName = stripMultipleSpaces(existingFullFileName[0:versionNumberMatch.start(1)] +
                existingFullFileName[versionNumberMatch.end(1):]).strip()
    else:
        # Check without being at end of string
        versionNumberMatch = VERSION_NUMBER.search(existingFullFileName)

        if versionNumberMatch:
            versionNumberString = versionNumberMatch.group(1).replace('_', '.')

            if '.' in versionNumber:
                versionNumber = versionNumberString
                # Decimal must be present in version number if it's not at the end of the line
                existingFullFileName = stripMultipleSpaces(existingFullFileName[0:versionNumberMatch.start(1)] +
                    existingFullFileName[versionNumberMatch.end(1):]).strip()

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

    strippedTitle = entry.title.replace(':', ' -')

    fileName = strippedTitle + versionNumber + '.' + extension

    if len(fileName) > 31:
        # print 'Filename ' + fileName + ' is too long. From ' + existingFullFileName
        shrunkFileName = fileName

        # Attempt to strip publisher/author name
        if entry.author is not None:
            for author in entry.author:
                shrunkFileName = stripStringFromString(author, shrunkFileName)

        if entry.publisher is not None:
            for publisher in entry.publisher:
                shrunkFileName = stripStringFromString(publisher, shrunkFileName)

        fileName = stripMultipleSpaces(shrunkFileName).strip()

        if len(fileName) > 31:
            # Attempt to strip between parens
            shrunkFileName = STRIP_PARENS.sub('', shrunkFileName)
            fileName = stripMultipleSpaces(shrunkFileName).strip()

        if len(fileName) > 31:
            # Attempt to strip before divider "-"
            split = shrunkFileName.split('-')
            if len(split) > 1:
                # Take all after first
                shrunkFileName = ' '.join(split[1:])

                fileName = stripMultipleSpaces(shrunkFileName).strip()

        if len(fileName) > 31:
            # Attempt to strip unneeded words
            for strippable in STRIPPABLE_WORDS:
                shrunkFileName = stripMultipleSpaces(stripStringFromString(strippable, shrunkFileName)).strip()
                if len(shrunkFileName) <= 31:
                    # Short circuit before removing all words if not necessary
                    break

            fileName = shrunkFileName

        if len(fileName) > 31:
            # Strip spacing
            shrunkFileName = shrunkFileName.replace(' ', '')
            fileName = shrunkFileName

        if len(fileName) <= 31:
            # print 'Successfully shrunk ' + fileName
            pass
        else:
            print 'Failed to shrink ' + fileName

    return fileName

def main():
    entries = loadEntries('1988.json')

    newEntries = []
    downloads = []

    for entry in entries:
        newEntry = copy.copy(entry)

        title = entry.title
        newTitle = title
        match = VERSION_NUMBER_END_OF_STRING.search(title)
        if match:
            versionNumber = match.group(1)
            if isYear(versionNumber):
                # Year, not version
                pass
            else:
                newTitle = stripMultipleSpaces(title[0:match.start(1)] + title[match.end(1):]).strip()

                newEntry.title = newTitle
                newEntry.version = versionNumber
        else:
            # Check without being at end of string
            match = VERSION_NUMBER.search(title)

            if match:
                versionNumber = match.group(1).replace('_', '.')

                if '.' in versionNumber:
                    # Decimal must be present in version number if it's not at the end of the line
                    newTitle = stripMultipleSpaces(title[0:match.start(1)] + title[match.end(1):]).strip()

                    newEntry.title = newTitle
                    newEntry.version = versionNumber

        directory = buildDirectory(entry)

        if hasattr(entry, 'downloads'):
            for download in entry.downloads:
                fileName = suggestFileName(newEntry, download)
                if fileName is None:
                    downloads.append('Invalid path' + ': ' + newTitle)
                else:
                    downloads.append(directory + fileName + ': ' + newTitle)
                osVersions = osVersionRange(download.version)

                if osVersions is not None:
                    download.minOs = osVersions[0]
                    download.maxOs = osVersions[1]

        newEntries.append(newEntry)

    save(newEntries, '1988modified.json')
    save(downloads, '1988downloads.json')

if __name__ == '__main__':
    main()
