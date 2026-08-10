# %%
from hoi4dev import *

N_COUNTRIES = 67

# %%
names = dict()
for c in range(N_COUNTRIES):
    tag = f"C{c:02d}"
    locs = ReadTxtLocs(pjoin(tag, "locs.txt"))
    name = locs[tag]['zh']
    names[tag] = name
SaveJson(names, "country_names_zh.json", indent=4)
names = dict()
for c in range(N_COUNTRIES):
    tag = f"C{c:02d}"
    locs = ReadTxtLocs(pjoin(tag, "locs.txt"))
    name = locs[tag]['en']
    names[tag] = name
SaveJson(names, "country_names.json", indent=4)

# %%