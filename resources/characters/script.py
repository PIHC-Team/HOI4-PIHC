# %%
from pyheaven import *
for f in ListFolders("./"):
    PrettifyJson(pjoin(f, "info.json"))
# %%
