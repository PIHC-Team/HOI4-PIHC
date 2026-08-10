# %%
from pyheaven import *

def get_all_modules(folder):
    return [f'MODULE_{m}' for f in ListFolders(folder, ordered=True) for m in ListFolders(pjoin(folder, f), ordered=True)]

def arrange_initial_conditions(modules):
    conditions = list()
    for m in modules:
        if 'SPECIAL' not in m:
            conditions.append(
                {
                    "module": m,
                    "count < 1": None,
                    "title": "ADVANCED_CHASSIS_REQUIRED_TOOLTIP"
                }
            )
    return conditions

# %%
conditions = arrange_initial_conditions(get_all_modules("tank"))
PrintJson(conditions)

# %%