import requests
import sys
import time
from bs4 import BeautifulSoup, NavigableString

from scrape import parsePage
from util import compact, getSoupFromPath, save

def scanForUrls(path):
    soup = getSoupFromPath(path)

    newPages = compact([extractUrl(element) for element in soup.find_all('h2')])
    newNavs = compact([extractUrl(element) for element in soup.find_all(class_='pager-item')])

    return (newPages, newNavs)

def extractUrl(domElement):
    element = domElement.find('a')

    if element is None:
        return None

    return element.get('href')

def downloadYear(year):
    yearString = str(year)

    examineUrl = '/year/' + yearString
    limit = -1

    navUrls = {}
    pageUrls = {}

    navUrls[examineUrl] = False

    newNavExamined = True
    count = 0
    while (newNavExamined and (limit == -1 or count < limit)):
        newNavExamined = False
        for url, examined in navUrls.iteritems():
            if not examined:
                time.sleep(2)
                try:
                    newPages, newNavs = scanForUrls(url)
                except:
                    print 'Exception occured ' + sys.exc_info()[0]
                    break

                for page in newPages:
                    if not page in pageUrls:
                        print 'Adding page ' + page
                        pageUrls[page] = False

                for nav in newNavs:
                    if not nav in navUrls:
                        print 'Adding nav ' + nav
                        navUrls[nav] = False

                navUrls[url] = True
                newNavExamined = True
                break

        count += 1

    print 'Examined ' + str(count) + ' nav pages'

    entries = []

    for path in pageUrls:
        time.sleep(2)
        try:
            entry = parsePage(path)
        except:
            print 'Exception occured ' + sys.exc_info()[0]
            break

        entries.append(entry)

    save(entries, 'data/' + yearString + '.json')

    print 'Downloaded ' + str(len(entries)) + ' applications'

def main():
    for year in range(1996, 2001):
        downloadYear(year)

if __name__ == "__main__":
    main()