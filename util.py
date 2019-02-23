import codecs
import json
import re
import requests
from bs4 import BeautifulSoup, NavigableString

BASE_URL = 'http://macintoshgarden.org'

STRIP_SPACES_AROUND_TAGS = re.compile(r'\s*(<[^<>]+>)\s*')
STRIP_MULT_SPACES = re.compile(r'\ +')

SPACE_BEFORE_PUNCT = set(['('])
SPACE_AFTER_PUNCT = set(['.', ',', '!', '?', '\"', ')'])

def compact(list):
    return [x for x in list if x is not None]

def concatStringsWithSpace(str1, str2):
    if str1 is None or len(str1) < 1:
        return str2

    if str2 is None or len(str2) < 1:
        return str1

    lastChar = str1[-1]
    firstChar = str2[0]

    if (lastChar.isalnum() or lastChar in SPACE_AFTER_PUNCT) and (firstChar.isalnum() or firstChar in SPACE_BEFORE_PUNCT):
        # Space is needed
        return str1 + ' ' + str2

    return str1 + str2

def stripMultipleSpaces(string):
    return STRIP_MULT_SPACES.sub(' ', string)

def firstOrNone(listObject):
    if len(listObject) > 0:
        return listObject[0]

    return None

def convertNone(o):
    if len(o) > 0:
        return o

    return None

def writeFile(text):
    f = codecs.open('download.html', 'w', 'utf-8')
    f.write(text)
    f.close()

def getFile():
    f = codecs.open('download.html', 'r', 'utf-8')
    text = f.read()
    f.close()
    return unicode(text)

class Encoder(json.JSONEncoder):
    def default(self, obj):
        return vars(obj)

def save(data, name='data.json'):
    with open(name, 'w') as outfile:
        json.dump(data, outfile, cls=Encoder)

def get(url):
    print 'Requesting url ' + url
    return requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:65.0) Gecko/20100101 Firefox/65.0'})

def getSoupFromPath(path):
    response = get(BASE_URL + path)
    text = response.text
    # writeFile(text)
    # text = getFile()

    # Replace newlines and tabs to prevent errors in string handling later
    text = text.translate({ord(c): ord(' ') for c in '\n\r\t'})
    text = text.replace('&nbsp;', ' ')
    text = STRIP_MULT_SPACES.sub(' ', text)
    text = STRIP_SPACES_AROUND_TAGS.sub('\g<1>', text)

    return BeautifulSoup(text, 'html5lib')