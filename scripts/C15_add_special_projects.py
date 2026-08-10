# ======================================== #
# === CHAPTER 15: Add Special Projects === #
# ======================================== #

# %%
# Import hoi4dev
from hoi4dev import *
# Fix the random seed
import numpy as np
np.random.seed(42)

def C15_add_special_projects(force=True):
    # %%
    # Let's first add all special project rewards. The resources of the special projects are located in `resources/special_projects/rewards/`.
    for sp_reward in TQDM(ListFolders("resources/special_projects/rewards", ordered=True), desc='Building special project rewards...'):
        path = pjoin("resources", "special_projects", "rewards", sp_reward)
        AddSPReward(path=path, translate=False)

    # %%
    # Now add all special projects. The resources of the characters are located in `resources/special_projects/projects/`.
    for sp_project in TQDM(ListFolders("resources/special_projects/projects", ordered=True), desc='Building special projects...'):
        path = pjoin("resources", "special_projects", "projects", sp_project)
        AddSP(path=path, translate=False, force=force)

# %%
if __name__=="__main__":
    C15_add_special_projects(force=True)