# ======================================== #
# ======= CHAPTER 15: Add Entities ======= #
# ======================================== #

# %%
# Import hoi4dev
from hoi4dev import *
# Fix the random seed
import numpy as np
np.random.seed(42)

def update_entities():
    CMD("cd ./resources/entities_autodiffuse/ && python autodiffuse.py")

def C16_add_entities(force=True):
    if force:
        update_entities()
    
    # %%
    UNITS_PATH = "./resources/copies/data/common/units/"
    ENTITIES_TYPES_TABLE = defaultdict(list)
    if (not force) and ExistFile("./resources/entities.json"):
        ENTITIES_TABLE = LoadJson("./resources/entities.json")
    else:
        # Priority 0: infantry / tank / air / cannon / ship
        for file_name in ["infantry", "tank", "air"]:
            sub_units = list(LoadJson(pjoin(UNITS_PATH, f"{file_name}.json"))['sub_units'].keys())
            for sub_unit in sub_units:
                ENTITIES_TYPES_TABLE[sub_unit].append(file_name)
        for file_name in ["engineer", "field_hospital", "military_police", "signal", "logistics"]:
            sub_units = list(LoadJson(pjoin(UNITS_PATH, f"{file_name}.json"))['sub_units'].keys())
            for sub_unit in sub_units:
                ENTITIES_TYPES_TABLE[sub_unit].append("infantry")
        for file_name in ["cannon"]:
            sub_units = list(LoadJson(pjoin(UNITS_PATH, f"{file_name}.json"))['sub_units'].keys())
            for sub_unit in sub_units:
                ENTITIES_TYPES_TABLE[sub_unit].append("cannon")
        for file_name in ["light_cruiser", "destroyer", "battleship", "battlecruiser", "carrier", "submarine"]:
            sub_units = list(LoadJson(pjoin(UNITS_PATH, f"{file_name}.json"))['sub_units'].keys())
            for sub_unit in sub_units:
                ENTITIES_TYPES_TABLE[sub_unit].append("ship")

        # Priority 1: PIHC air units types
        for tag in ["balloon", "galleon", "airship", "plane", "ufo"]:
            for sub_unit in ENTITIES_TYPES_TABLE:
                if sub_unit.startswith(tag):
                    ENTITIES_TYPES_TABLE[sub_unit].append(tag)
        # Priority 1: PIHC land units types
        for sub_unit in ENTITIES_TYPES_TABLE:
            if ('tank' in ENTITIES_TYPES_TABLE[sub_unit]) and (sub_unit not in ['tank_light', 'tank_medium', 'tank_heavy']):
                ENTITIES_TYPES_TABLE[sub_unit].append("titan")
        for file_name in ["engineer", "field_hospital", "military_police", "signal", "logistics"]:
            sub_units = list(LoadJson(pjoin(UNITS_PATH, f"{file_name}.json"))['sub_units'].keys())
            for sub_unit in sub_units:
                ENTITIES_TYPES_TABLE[sub_unit].append(file_name)
        # Priority 1: PIHC sea units types
        for file_name in ["light_cruiser", "destroyer", "battleship", "battlecruiser", "carrier", "submarine"]:
            sub_units = list(LoadJson(pjoin(UNITS_PATH, f"{file_name}.json"))['sub_units'].keys())
            for sub_unit in sub_units:
                ENTITIES_TYPES_TABLE[sub_unit].append(file_name)

        def deduce_entity_type_from_name(f):
            types = list()
            if f.startswith("TANK"): types.append("tank")
            if f.startswith("CANNON"): types.append("cannon")
            if f.startswith("SHIP"): types.append("ship")
            if f.startswith("AIR") or f.startswith("AIRFRAME"): types.append("air")
            if f.startswith("TITAN") or f.startswith("TANK_TITAN"): types.append("titan")
            if f.startswith("RANGED"): types.append("infantry_traditional")
            if f.startswith("SHIELD"): types.append("infantry_shield")
            if f.startswith("AUTOMATA"): types.append("infantry_automata")
            if f.startswith("WITCHCRAFT"): types.append("infantry_magical")
            if f.startswith("MAGICAL"): types.append("infantry_magical")
            if f.startswith("SPECIAL"): types.append("infantry")
            if f.startswith("VEHICLE"): types.append("infantry_motorized")
            # Air
            if f.startswith("MISSILE"): types.append("missile")
            if "BALLOON" in f: types.append("balloon")
            if "GALLEON" in f: types.append("galleon")
            if "AIRSHIP" in f: types.append("airship")
            if "PLANE" in f: types.append("plane")
            if "UFO" in f: types.append("ufo")
            if f.startswith("AIR") and ('FIXEDWING' in f): types.append("plane")
            if f.startswith("AIR") and ('CLOUD' in f): types.append("galleon")
            # Land
            if f.startswith("TANK") and "LIGHT" in f: types.append("tank_light")
            if f.startswith("TANK") and "MEDIUM" in f: types.append("tank_medium")
            if f.startswith("TANK") and "HEAVY" in f: types.append("tank_heavy")
            if f.startswith("CANNON") and "LIGHT" in f: types.append("cannon_light")
            if f.startswith("CANNON") and "MEDIUM" in f: types.append("cannon_medium")
            if f.startswith("CANNON") and "HEAVY" in f: types.append("cannon_heavy")
            # Era
            if f.endswith("WOODEN") or f.endswith("STEEL"): types.append("ancient")
            if f.endswith("STEAM"): types.append("steam")
            if f.endswith("MODERN") or f.endswith("OIL") or f.endswith("IMPROVED"): types.append("oil")
            if f.endswith("CONTEMPORARY") or f.endswith("ELEC") or f.endswith("ADVANCED"): types.append("elec")
            return types

        # Priority 2: Equipment Archetypes
        for f in ListFolders("./resources/equipments/archetypes", ordered=True):
            ENTITIES_TYPES_TABLE[f"ARCHETYPE_{f}"] = deduce_entity_type_from_name(f)

        # Priority 3: Equipment Types
        for f in ListFolders("./resources/equipments/equipments", ordered=True):
            ENTITIES_TYPES_TABLE[f"EQUIPMENT_{f}"] = deduce_entity_type_from_name(f)

        # Supplements
        for t in ENTITIES_TYPES_TABLE:
            if not ENTITIES_TYPES_TABLE[t]:
                ENTITIES_TYPES_TABLE[t].append("infantry")
            if t not in ENTITIES_TYPES_TABLE[t]:
                ENTITIES_TYPES_TABLE[t].append(t)
            
        ENTITIES_TYPES_TABLE = {k: list(v) for k, v in ENTITIES_TYPES_TABLE.items()}
        ENTITIES_TABLE = {"all_tags": sorted(list(set(sum(list(v for v in ENTITIES_TYPES_TABLE.values()), [])))), "types": ENTITIES_TYPES_TABLE}
        SaveJson(ENTITIES_TABLE, "./resources/entities.json", indent=4)
    # %%
    AddModels("./resources/entities/", units_pool=ENTITIES_TABLE["types"])

# %%
if __name__=="__main__":
    C16_add_entities(force=True)