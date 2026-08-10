# ======================================= #
# ==== CHAPTER 2: Add Mirror Portals ==== #
# ======================================= #
# %%
# Sometimes writing some code may be necessary~
# The PIHC mod has mirror portals as a feature, so we write some code to support it.
from hoi4dev import *
import itertools
import pandas as pd
MIRROR_PROVINCES = [
    4359, # Foreverfree Forest
    14927, # Storm King Island
    1133, # Dragonland
    15080, # Yaks and Reindeers
    5800, # Cloud Sea
    5772, # Windigo
    3688, # Crystal Empire
    15094, # Tartarus
]

RAILWAY_PROVINCES = [
    ( 6357, 10251), # Northern Railway
    (10210, 10312),
    (10312, 10115),
    (10080,  5772),
    (12218, 12256), # Griffonica to Kirinthal
    ( 1235, 12377),
    ( 6287, 15093),
    (15093,  9318),
    ( 3699, 12585),
]

# %%
def AddMirrorPortals():
    adjs = pd.read_csv(F("map/adjacencies_backup.csv"), sep=';')
    adjs = adjs.drop(adjs.tail(1).index)
    for s, t in itertools.permutations(MIRROR_PROVINCES, 2):
        new_row = pd.DataFrame([[s, t, 'sea', s, -1, -1, -1, -1, '', 'MirrorPortal']], columns=adjs.columns)
        adjs = pd.concat([adjs, new_row], ignore_index=True)
    adjs.to_csv(F("map/adjacencies.csv"), sep=';', index=False, lineterminator='\r\n')
    with open(F("map/adjacencies.csv"), 'a') as f:
        f.write('-1;-1;;-1;-1;-1;-1;-1;-1') 
        
    provs = pd.read_csv(F("map/definition_backup.csv"), sep=';', header=None)
    provs[5] = provs[5].astype('str')
    for s in MIRROR_PROVINCES:
        for i, r in provs.iterrows():
            provs.at[i, 5] = r[5].lower()
    for s in MIRROR_PROVINCES:
        for i, r in provs.iterrows():
            if r[0] == s:
                provs.at[i, 6] = 'mirrors_terrain'
    provs.to_csv(F("map/definition.csv"), sep=';', index=False, header=False, lineterminator='\r\n')

def AddContinentalRailways():
    adjs = pd.read_csv(F("map/adjacencies_backup.csv"), sep=';')
    adjs = adjs.drop(adjs.tail(1).index)
    for s, t in RAILWAY_PROVINCES:
        new_row = pd.DataFrame([[s, t, 'sea', s, -1, -1, -1, -1, '', 'ContinentalRailway']], columns=adjs.columns)
        adjs = pd.concat([adjs, new_row], ignore_index=True)
    adjs.to_csv(F("map/adjacencies.csv"), sep=';', index=False, lineterminator='\r\n')
    with open(F("map/adjacencies.csv"), 'a') as f:
        f.write('-1;-1;;-1;-1;-1;-1;-1;-1') 
        
    provs = pd.read_csv(F("map/definition_backup.csv"), sep=';', header=None)
    provs[5] = provs[5].astype('str')
    for s in MIRROR_PROVINCES:
        for i, r in provs.iterrows():
            provs.at[i, 5] = r[5].lower()
    provs.to_csv(F("map/definition.csv"), sep=';', index=False, header=False, lineterminator='\r\n')

# %%
def C02_add_mirror_portal(force=True):
    if force or not ExistFile(F("map/adjacencies.csv")):
        AddMirrorPortals()

# %%
def C02_add_continental_railways(force=True):
    if force or not ExistFile(F("map/adjacencies.csv")):
        AddContinentalRailways()

# %$
def C02_normal(force=True):
    if force or not ExistFile(F("map/adjacencies.csv")):
        CopyFile(F("map/adjacencies_backup.csv"), F("map/adjacencies.csv"))

# The Mirror portals come with a new terrain, it is contained in the `resources/copies/data/common/terrain` folder.
if __name__=="__main__":
    C02_add_continental_railways(force=True)