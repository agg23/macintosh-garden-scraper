import os
import shutil
import subprocess
import sys

from buildDirectories import makeDirectory

def getFileList(path):
    try:
        fileListString = subprocess.check_output(['.\Unarchiver\lsar', path], shell=True).decode(sys.stdout.encoding)
    except:
        return []

    fileList = fileListString.split(os.linesep)

    # First line is format information
    fileList = fileList[1:]

    return fileList

def main():
    if len(sys.argv) != 2:
        print 'Invalid arguments. Please specify a file to decompress'
        return
    
    filePath = sys.argv[1]

    fullFileName = os.path.basename(filePath)
    index = fullFileName.index('.')
    archiveName = fullFileName[:index]

    outputFolder = archiveName + '/'
    appledoublePath = outputFolder + '.AppleDouble/'

    fileList = getFileList(filePath)

    # Actually decompress
    subprocess.check_call(['.\Unarchiver\unar', filePath])

    # Build Netatalk AppleDouble setup
    for fileName in fileList:
        fileName = fileName.strip()

        if fileName == '':
            continue

        resourceFork = outputFolder + fileName + '.rsrc'

        if os.path.isfile(resourceFork):
            makeDirectory(appledoublePath)
            shutil.move(resourceFork, appledoublePath + fileName)
            # Touch non-resource fork file in case it doesn't exist
            open(outputFolder + fileName, 'a').close()

if __name__ == '__main__':
    main()