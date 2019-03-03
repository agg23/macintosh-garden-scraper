import re

from util import isYear, stringRemoveCenter, stripMultipleSpaces, stripStringFromString

EXTENSION_END_OF_STRING_VERSION_NUMBER = r'(\.[_a-z]*)*$'
VERSION_NUMBER_MAIN = r'(([0-9]|\.(?=[0-9])|v(?=[0-9]))([0-9]|[._](?=[0-9]|x(?=\b|\s)))*([a-z](?=[0-9.]|\b))?)'
ROMAN_NUMERAL = r'(\b|[_.-])(i{1,4})(\b|[_.-])'

VERSION_NUMBER = re.compile(VERSION_NUMBER_MAIN, re.IGNORECASE)
VERSION_NUMBER_END_OF_STRING = re.compile(VERSION_NUMBER_MAIN + EXTENSION_END_OF_STRING_VERSION_NUMBER, re.IGNORECASE)
ROMAN_NUMERAL_END_OF_STRING = re.compile(ROMAN_NUMERAL, re.IGNORECASE)
ARCHITECTURE = re.compile(r'(ppc|(?<![0-9])68k?)')

STRIP_PARENS = re.compile(r'(\([a-z0-9./ -\'"]*\))', re.IGNORECASE)

STRIPPABLE_WORDS = ['macintosh', 'inc.', 'inc', 'incorporated', 'corp', 'volume', 'aka', 'the', 'an',
    'a', 'is', '&', '%', '$', '#', '@', 'and', 'or', 'of', 'in', 'for']

def cleanupString(string):
    return stripMultipleSpaces(string).strip()

def stripBetweenParens(string):
    if len(string) > 31:
        # Attempt to strip between parens
        newString = STRIP_PARENS.sub('', string)
        return cleanupString(newString)

    return string

def stripFirstHyphen(string):
    if len(string) > 31:
        # Attempt to strip before divider "-"
        split = string.split('-')
        if len(split) > 1:
            # Take all after first
            newString = ' '.join(split[1:])

            return cleanupString(newString)

    return string

def stripStringsFromString(stringsList, string):
    if stringsList is not None:
        newString = string
        for replaceString in stringsList:
            newString = stripStringFromString(replaceString, newString)

        return cleanupString(newString)

    return string

def stripStringsFromStringIfNeeded(stringsList, string):
    if len(string) > 31:
        return stripStringsFromString(stringsList, string)

    return string

def stripStrippableWords(string):
    if len(string) > 31:
        # Attempt to strip unneeded words
        newString = string
        for strippable in STRIPPABLE_WORDS:
            newString = cleanupString(stripStringFromString(strippable, newString))
            if len(newString) <= 31:
                # Short circuit before removing all words if not necessary
                break

        return newString

    return string

def stripSpacing(string):
    if len(string) > 31:
        # Strip spacing
        return string.replace(' ', '')

    return string

def stripFirstWords(string, stringWithSpaces):
    if len(string) > 31:
        newString = stringWithSpaces

        split = stringWithSpaces.split(' ')
        for i in range(1, len(split)):
            newString = ''.join(split[i:])

            if len(newString) <= 31:
                break

        return newString
    
    return string

def extractVersionNumber(string, includeRomanNumeral=False):
    versionNumberMatch = VERSION_NUMBER_END_OF_STRING.search(string)

    if versionNumberMatch:
        versionNumberString = versionNumberMatch.group(1)
        if not isYear(versionNumberString):
            # Any underscores should be periods instead
            versionNumber = versionNumberString.replace('_', '.')
            # Strip version number from filename
            newString = cleanupString(stringRemoveCenter(string, versionNumberMatch.start(1), versionNumberMatch.end(1)))

            return (versionNumber, newString)
    else:
        # Check for Roman numerals at end of string
        versionNumberMatch = ROMAN_NUMERAL_END_OF_STRING.search(string)

        if includeRomanNumeral and versionNumberMatch:
            versionNumber = versionNumberMatch.group(2)

            newString = cleanupString(stringRemoveCenter(string, versionNumberMatch.start(2), versionNumberMatch.end(2)))

            return (versionNumber, newString)

        else:
            # Check without being at end of string
            versionNumberMatch = VERSION_NUMBER.search(string)

            if versionNumberMatch:
                versionNumberString = versionNumberMatch.group(1).replace('_', '.')

                if '.' in versionNumberString:
                    # Decimal must be present in version number if it's not at the end of the line
                    versionNumber = versionNumberString
                    newString = cleanupString(stringRemoveCenter(string, versionNumberMatch.start(1), versionNumberMatch.end(1)))

                    return (versionNumber, newString)

    return (None, string)

def extractArchitecture(string):
    architectureMatch = ARCHITECTURE.search(string)

    if architectureMatch:
        architectureString = architectureMatch.group(1)
        if architectureString == '68':
            architectureString = '68k'

        return architectureString

    return None
