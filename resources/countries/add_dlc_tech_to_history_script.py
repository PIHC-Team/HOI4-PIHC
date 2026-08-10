# %%
from hoi4dev import *

N_COUNTRIES = 67

def add_dlc_tech_to_history(DLC, TECH, REQUIREMENTS=list()):
    for tag in [f"C{i:02d}" for i in range(N_COUNTRIES)]:
        info_path = pjoin(tag, "info.json")
        info = LoadJson(info_path)
        if ('history' in info) and ('set_technology' in info['history']) and all((r in info['history']['set_technology']) for r in REQUIREMENTS):
            for if_clause in dup_gen('if'):
                if (if_clause in info['history']) and info['history'][if_clause]['limit'] == {'has_dlc': DLC}:
                    info['history'][if_clause] = merge_dicts([info['history'][if_clause], {'set_technology': {TECH: 1}}], d=True)
                    break
                elif (if_clause not in info['history']):
                    info['history'][if_clause] = {'limit': {'has_dlc': DLC}, 'set_technology': {TECH: 1}}
                    break
        SaveJson(info, info_path, indent=4)

# %%
add_dlc_tech_to_history("No Step Back", "TECHNOLOGY_NSB_CHASSIS_TANK_LIGHT_WOODEN", REQUIREMENTS=["TECHNOLOGY_VEHICLE_I", "TECHNOLOGY_VEHICLE_II"])
# %%
