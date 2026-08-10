from hoi4dev import *

for folder in ListFolders("./"):
    if folder.startswith("ENABLE_"):
        locs = ReadTxt(pjoin(folder, "locs.txt"))
        locs = locs.replace('允许', '启用')
        SaveTxt(locs, pjoin(folder, "locs.txt"))