from util import hasKeys

ENTRY_KEYS = ['source', 'title', 'type']
APPLICATION_KEYS = ['name', 'size', 'version']
RATING_KEYS = ['average', 'count']

class JSONInitable(object):
    def __init__(self, json):
        self.__dict__ = json

class Entry(JSONInitable):
    def __init__(self, source, title, typeString, category, year, author, publisher, description, architecture):
        self.source = source
        self.title = title
        self.type = typeString
        self.category = category
        self.year = year
        self.author = author
        self.publisher = publisher
        self.description = description
        self.architecture = architecture

class Application(JSONInitable):
    def __init__(self, name, size, versionString):
        self.name = name
        self.size = size
        self.version = versionString

class Rating(JSONInitable):
    def __init__(self, average, count):
        self.average = average
        self.count = count

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
