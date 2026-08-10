# %%
from hoi4dev import *

# %%
def create_clone_entity(source, target):
    return {
        "clone": source,
        "name": target
    }

# %%
PIHC_entities_mapping = {
    # "light_armor_entity": "light_armor_entity",
    # "medium_armor_entity": "medium_armor_entity",
    # "heavy_armor_entity": "heavy_armor_entity",
    # "super_heavy_armor_entity": "super_heavy_armor_entity",
    # "light_plane_entity": "light_plane_entity",
    # "medium_plane_entity": "medium_plane_entity",
    # "jet_plane_entity": "jet_plane_entity",
    "infantry_entity": "infantry_entity",
    "infantry_2_entity": "infantry_2_entity",
    "infantry_3_entity": "infantry_3_entity",
    "vehicle_infantry_rifle_entity": "vehicle_infantry_rifle_entity",
    "vehicle_infantry_mg_entity": "vehicle_infantry_mg_entity",
    "motorized_entity": "motorized_entity",
    "mechanized_entity": "mechanized_entity",
    "artillery_entity": "artillery_entity",
    "anti_tank_entity": "anti_tank_entity",
}

# %%
PIHC_country_entity_mapping = {
    "CHN": "GER",
    "C01": "EQS",
    "C02": "EQS",
    "C03": "EQS",
    "C04": "EQS",
    "C05": "EQS",
    "C06": "EQS",
    "C07": "EQS",
    "C08": "STG",
    "C09": "EQS",
    "C10": "EQS",
    "C11": "CHN",
    "C12": "EQS",
    "C13": "EQS",
    "C14": "EQS",
    "C15": "CRY",
    "C16": "EQS",
    "C17": "deer_gfx",
    "C18": "EQS",
    "C19": "GRI",
    "C20": "EQS",
    "C21": "EQS",
    "C22": "EQS",
    "C23": "EQS",
    "C24": "EQS",
    "C25": "EQS",
    "C26": "EQS",
    "C27": "EQS",
    "C28": "EQS",
    "C29": "EQS",
    "C30": "ZES",
    "C31": "EQS",
    "C32": "EQS",
    "C33": "EQS",
    "C34": "EQS",
    "C35": "EQS",
    "C36": "EQS",
}

# %%
entities = dict()
entities[find_dup("entity", entities)] = create_clone_entity(f"EQC_artillery_entity", f"EQS_artillery_entity")
for tgt, src in PIHC_country_entity_mapping.items():
    for tgt_entity, src_entity in PIHC_entities_mapping.items():
        entities[find_dup("entity", entities)] = create_clone_entity(f"{src}_{src_entity}", f"{tgt}_{tgt_entity}")
with open("zz_pihc_entities.asset", "w", encoding='utf-8', errors='ignore') as f:
    f.write(Dict2CCL(entities)+"\n")
    
# %%