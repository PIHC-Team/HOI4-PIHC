# %%
from hoi4dev import *

SOURCE = "/Users/magolor/Library/Application Support/Steam/steamapps/common/Hearts of Iron IV/localisation"
REV_MAPPING = {
    'simp_chinese': 'zh',
    'english': 'en'
}

import re
def split_by_pattern(text):
    pattern = r':\d*'
    parts = re.split(pattern, text)
    key, value = [p.strip() for p in parts]
    value = value.strip('"').strip("'")
    return key, value

def search_keyword(keywords):
    locs = dict()
    for lang in ['english', 'simp_chinese']:
        locs[lang] = [f for f in ListFiles(pjoin(SOURCE,lang)) if f.endswith(".yml")]

    loaded_locs = dict()
    for lang, loc in locs.items():
        for name in loc:
            new_data = ReadYmlLocs(pjoin(SOURCE, lang, name))
            for key in new_data:
                if key in loaded_locs:
                    loaded_locs[key][REV_MAPPING[lang]] = new_data[key][REV_MAPPING[lang]]
                else:
                    loaded_locs[key] = {REV_MAPPING[lang]: new_data[key][REV_MAPPING[lang]]}
    
    new_locs = dict()
    for key in loaded_locs:
        for lang in keywords:
            for pattern, replace in keywords[lang]:
                if (lang in loaded_locs[key]) and (pattern in loaded_locs[key][lang]):
                    if key not in new_locs:
                        new_locs[key] = {}
                    if lang in new_locs[key]:
                        new_locs[key][lang] = new_locs[key][lang].replace(pattern, replace)
                    else:
                        new_locs[key][lang] = loaded_locs[key][lang].replace(pattern, replace)
    return new_locs

# %%
new_locs = search_keyword(keywords = {
    'zh': [
        ("人海", "马海"),
    ]
})
del_keys = list()
for key in new_locs:
    if len(key) >= 4 and key[3]=='_' and key[0:3].upper()==key[0:3]:
        del_keys.append(key)
new_locs = {k: new_locs[k] for k in new_locs if k not in del_keys}
SaveTxtLocs(new_locs, "./zh_human.txt")
# %%
