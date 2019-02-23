from bs4 import BeautifulSoup, NavigableString

from entry import Entry, Application, Rating
from util import compact, concatStringsWithSpace, convertNone, firstOrNone, getSoupFromPath

STRINGLESS_CLASSES = set(['download'])
NEWLINE_TAGS = set(['p', 'br'])
TEXT_TAGS = set(['a', 'i', 'b', 'strong'])

def parsePage(path):
    pathList = path.split('/')

    if len(pathList) < 2:
        print 'Invalid URL'
        return None

    typeString = pathList[1]

    soup = getSoupFromPath(path)

    h1Title = soup.find('h1')
    if h1Title is None:
        return None
    title = unicode(h1Title.string)

    # Get metadata
    rating = parseRating(soup)

    metadataList = compact([parseMetadataTableRow(row) for row in soup.find(class_='descr').find_all('tr')])
    metadata = dict(metadataList)

    downloads = [parseDownloadRow(row) for row in soup.find_all(class_='download')]

    manuals = [parseManualRow(row) for row in soup.find_all(class_='manual')]

    descriptionAndCompatability = parseDescriptionAndCompatability(soup)

    return buildEntry(path, typeString, title, rating, metadata, downloads, manuals, descriptionAndCompatability)

def parseRating(soup):
    averageRating = soup.find(class_='average-rating')
    totalVotes = soup.find(class_='total-votes')

    if averageRating is None or totalVotes is None:
        return None

    averageSpan = averageRating.find('span')
    average = unicode(averageSpan.string)

    totalSpan = totalVotes.find('span')
    total = unicode(totalSpan.string)

    return (average, total)

def parseMetadataTableRow(row):
    columns = row.find_all('td')

    if len(columns) != 2:
        print 'Unexpected number of description columns'
        return None
    
    metadataType = unicode(columns[0].find('strong').string).lower().strip(':')

    if metadataType.lower() == 'rating':
        # Skip (special handling for rating)
        return None

    metadataValues = [unicode(a.string) for a in columns[1].find_all('a')]

    return (metadataType, metadataValues)

def parseDownloadRow(row):
    nameTag = row.find('small', recursive=False)
    name = extractElementText(nameTag)
    size = extractString(nameTag, 'i')
    if size is not None:
        size = size.strip('()')
    versionString = extractElementText(row)

    return Application(name, size, versionString)

def parseManualRow(row):
    nameTag = row.find('small', recursive=False)
    name = extractElementText(nameTag)

    return name

def parseDescriptionAndCompatability(soup):
    gamePreview = soup.find(class_='game-preview')

    foundStrings = []

    element = gamePreview.nextSibling
    while (element is not None):
        if isinstance(element, NavigableString):
            foundStrings.append(unicode(element))
        else:
            if element.get('id') == 'comments':
                # End of section
                break

            foundStrings.extend(flattenAndCombineStringTags(element))
        
        element = element.nextSibling

    compatibility = False
    firstDescription = True
    firstCompatibility = True

    description = ''
    architecture = ''
    compatibilityText = ''

    for string in foundStrings:
        string = string.strip()

        isCompatibility = False
        if not compatibility and string == 'Compatibility':
            isCompatibility = True
            compatibility = True

        if compatibility:
            if string.startswith('Architecture:'):
                architecture = string[13:].strip()
            else:
                if not firstCompatibility:
                    compatibilityText += '\n'
                if not isCompatibility:
                    compatibilityText += string
                    firstCompatibility = False
        else:
            if not firstDescription:
                description += '\n'
            description += string
            firstDescription = False

    return (description, architecture, compatibilityText)

def flattenAndCombineStringTags(domElement):
    foundStrings = []
    currentString = ''

    if domElement.get('class') and any(className in STRINGLESS_CLASSES for className in domElement.get('class')):
        # Skip this element
        return []

    # Recursively examine current tag
    for element in domElement.children:
        if isinstance(element, NavigableString):
            currentString = concatStringsWithSpace(currentString, unicode(element))
        elif element.get('class') and any(className in STRINGLESS_CLASSES for className in element.get('class')):
            # Skip this element
            break
        elif element.name in NEWLINE_TAGS:
            if currentString != '':
                foundStrings.append(currentString)
                currentString = ''
            foundStrings.extend(flattenAndCombineStringTags(element))
        elif element.name in TEXT_TAGS:
            strings = flattenAndCombineStringTags(element)
            length = len(strings)
            if length > 1:
                # Use formatting provided by lower level
                if currentString != '':
                    foundStrings.append(currentString)
                    currentString = ''
                foundStrings.extend(strings)
            elif length == 1:
                currentString = concatStringsWithSpace(currentString, strings[0])
        else:
            foundStrings.extend(flattenAndCombineStringTags(element))

    # Save last string
    if currentString != '':
        foundStrings.append(currentString)

    return foundStrings

def extractString(domElement, tagName, index=-1, recursive=True):
    if domElement is None:
        return None

    if index > -1:
        elementList = domElement.find_all(tagName, recursive=recursive)
        if len(elementList) > index:
            element = elementList[index]
        else:
            return None
    else:
        element = domElement.find(tagName, recursive=recursive)

    if element is None:
        return None

    return unicode(element.string).strip()

def extractElementText(domElement):
    if domElement is None:
        return None

    element = domElement.find(text=True, recursive=False)

    if element is None:
        return None

    return unicode(element.string).strip()

def buildEntry(source, typeString, title, rating, metadata, downloads, manuals, descriptionAndCompatability):
    category = convertNone(metadata.get('category'))
    year = firstOrNone(metadata.get('year released'))
    author = convertNone(metadata.get('author'))
    publisher = convertNone(metadata.get('publisher'))

    description = convertNone(descriptionAndCompatability[0])
    architecture = convertNone(descriptionAndCompatability[1])
    compatibilityText = convertNone(descriptionAndCompatability[2])

    if year is not None:
        year = int(year, base=10)

    entry = Entry(source, title, typeString, category, year, author, publisher, description, architecture)

    if rating is not None:
        entryRating = Rating(float(rating[0]), int(rating[1], base=10))
        entry.rating = entryRating

    entry.compatibilityText = compatibilityText
    
    if len(downloads) > 0:
        entry.downloads = downloads
    
    if len(manuals) > 0:
        entry.manuals = manuals

    return entry

print vars(parsePage('/apps/learnps'))