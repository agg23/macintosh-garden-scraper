class Entry(object):
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

class Application(object):
    def __init__(self, name, size, versionString):
        self.name = name
        self.size = size
        self.version = versionString

class Rating(object):
    def __init__(self, average, count):
        self.average = average
        self.count = count
