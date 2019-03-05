from internetarchive import get_item, download

def downloadAlphaWithPrefix(prefix):
    for charCode in range(65, 92):
        if charCode == 91:
            # Use for number
            charCode = 48
        char = chr(charCode)
        download(prefix + char, glob_pattern='*.torrent', no_directory=True, destdir='C:/Users/adam/Desktop/IA')

downloadAlphaWithPrefix('Macintosh_Garden_Apps_Collection_')
