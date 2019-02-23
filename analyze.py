import copy
import json
import re

from entry import Entry, Application, Rating
from util import save, stripMultipleSpaces

VERSION_NUMBER = re.compile(r'\b\s+([0-9.][0-9.a-zA-z]*)')

ENTRY_KEYS = ['source', 'title', 'type']
APPLICATION_KEYS = ['name', 'size', 'version']
RATING_KEYS = ['average', 'count']

def jsonDecode(dictionary):
    if hasKeys(dictionary, ENTRY_KEYS):
        entry = Entry(dictionary.get('source'), dictionary.get('title'), dictionary.get('category'), dictionary.get('type'),
            dictionary.get('year'), dictionary.get('author'), dictionary.get('publisher'), dictionary.get('description'), dictionary.get('architecture'))

        rating = dictionary.get('rating')
        if rating is not None:
            entry.rating = rating

        entry.compatibilityText = dictionary.get('compatabilityText')

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

def main():
    entries = loadEntries('1988.json')

    newEntries = []

    for entry in entries:
        newEntry = copy.copy(entry)

        title = entry.title
        match = VERSION_NUMBER.search(title)
        if match:
            versionNumber = match.group(1)
            newTitle = stripMultipleSpaces(title[0:match.start(1)] + title[match.end(1):len(title)])

            newEntry.title = newTitle
            newEntry.version = versionNumber

        newEntries.append(newEntry)

    save(newEntries, '1988modified.json')

if __name__ == '__main__':
    main()
