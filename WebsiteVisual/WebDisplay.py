import os
from pathlib import Path
cwd = Path.cwd()
mod_path = Path(__file__).parent

def getDjangoPath():
    relpath = '../Django/theGrinch/website/templates'
    srcpath = (mod_path / relpath).resolve()
    newPath = str(srcpath)
    return newPath
