# %%
from pyheaven import *
positions = [
    (-1,-1),    #  0
    ( 8, 0),    #  1
    ( 6, 4),    #  2
    (12, 6),    #  3
    ( 6, 1),    #  4
    (12, 5),    #  5
    ( 3, 2),    #  6
    (10, 0),    #  7
    ( 7, 5),    #  8
    ( 7, 6),    #  9
    ( 9, 7),    # 10
    (10, 2),    # 11
    (13, 3),    # 12
    ( 4, 4),    # 13
    (12, 1),    # 14
    (11, 8),    # 15
    ( 9, 8),    # 16
    ( 4, 1),    # 17
    (10, 4),    # 18
    ( 7, 3),    # 19
    ( 4, 6),    # 20
    ( 9, 5),    # 21
    ( 3, 3),    # 22
    ( 7, 8),    # 23
    (12, 4),    # 24
    ( 7, 7),    # 25
    ( 4, 5),    # 26
    ( 6, 0),    # 27
    (11, 7),    # 28
    ( 5, 7),    # 29
    ( 8, 4),    # 30
    ( 5, 8),    # 31
    ( 9, 6),    # 32
    (13, 2),    # 33
]
for t in range(4, 34):
    name = f"C03_MUFFIN_{t:02d}"
    CopyFolder("C03_MUFFIN_01", name)
    info = LoadJson(pjoin(name, "info.json"))
    info['completion_reward'] = {
        'hidden_effect': {"mark_focus_tree_layout_dirty": True},
        'custom_effect_tooltip': f"FOCUS_C03_MUFFIN_{t:02d}_TOOLTIP",  
    }
    info['allow_branch'] = {
        "has_completed_focus": f"FOCUS_C03_MUFFIN_{t-1:02d}"
    }
    info['x'] = positions[t][0]; info['y'] = positions[t][1]
    SaveJson(info, pjoin(name, "info.json"), indent=4)
# %%
