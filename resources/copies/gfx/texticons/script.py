# %%
from hoi4dev import *

folder = "../interface/counters/divisions_small/"

for file in ListFiles(folder):
    if file.startswith("onmap_unit_cannon_"):
        img = ImageLoad(folder + file)
        id = file.split("_",3)[-1].split('_icon')[0]
        img.crop(0, 0, 30, 12)
        ImageSave(img, f"./unit_category_artillery_{id}_icon_small.dds")
# %%
