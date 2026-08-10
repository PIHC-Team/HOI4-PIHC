# ============================= #
# ==== CHAPTER 3: Add GFXs ==== #
# ============================= #

# %%
# Import hoi4dev
from hoi4dev import *
# Fix the random seed
import numpy as np
np.random.seed(42)

def C03_add_gfxs(force=True):
    # %%
    # Loadingscreens
    path = pjoin('hoi4dev_settings', 'imgs', 'loadingscreens')
    files = [f for f in ListFiles(path, ordered=True) if f.endswith('.png')]
    # main = "05 Grogal's Bell (4K).png" # v0.2.0
    # main = "15 Tricks Behind The Curtain (4K).png" # v0.2.1
    # main = "20 Kirins (4K).png" # v0.2.2
    main = "25 Maledix Lapis (4K).png" # v0.2.3
    assert(main in files)
    images = [ImageLoad(pjoin(path,f)) for f in files if f != main]
    SetLoadingScreenImages(images, main=ImageLoad(pjoin(path,main)))

# %%
if __name__=="__main__":
    C03_add_gfxs(force=True)