# %%
from pyheaven import *

template = """
[en.C04_SKY_STINGER_INC_{i}]
§YSky Stinger & Vapor Trail§!’s support §G+{j:.2f}%§!
[zh.C04_SKY_STINGER_INC_{i}]
§Y破空&雾轨§!支持度 §G+{j:.2f}%§!
[en.C04_SKY_STINGER_DEC_{i}]
§YSky Stinger & Vapor Trail§!’s support §R-{j:.2f}%§!
[zh.C04_SKY_STINGER_DEC_{i}]
§Y破空&雾轨§!支持度 §R-{j:.2f}%§!
[en.C04_SKY_STINGER_GE_{i}]
§YSky Stinger & Vapor Trail§! has support no less than §Y{j:.2f}%§!
[zh.C04_SKY_STINGER_GE_{i}]
§Y破空&雾轨§!支持度不低于 §Y{j:.2f}%§!
[en.C04_SKY_STINGER_LE_{i}]
§YSky Stinger & Vapor Trail§! has support no more than §Y{j:.2f}%§!
[zh.C04_SKY_STINGER_LE_{i}]
§Y破空&雾轨§!支持度不高于 §Y{j:.2f}%§!

[en.C04_WIND_RIDER_INC_{i}]
§YWind Rider§!’s support §G+{j:.2f}%§!
[zh.C04_WIND_RIDER_INC_{i}]
§Y乘风§!支持度 §G+{j:.2f}%§!
[en.C04_WIND_RIDER_DEC_{i}]
§YWind Rider§!’s support §R-{j:.2f}%§!
[zh.C04_WIND_RIDER_DEC_{i}]
§Y乘风§!支持度 §R-{j:.2f}%§!
[en.C04_WIND_RIDER_GE_{i}]
§YWind Rider§! has support no less than §Y{j:.2f}%§!
[zh.C04_WIND_RIDER_GE_{i}]
§Y乘风§!支持度不低于 §Y{j:.2f}%§!
[en.C04_WIND_RIDER_LE_{i}]
§YWind Rider§! has support no more than §Y{j:.2f}%§!
[zh.C04_WIND_RIDER_LE_{i}]
§Y乘风§!支持度不高于 §Y{j:.2f}%§!

[en.C04_WASHOUTS_INC_{i}]
§YThe Washouts§!’ support §G+{j:.2f}%§!
[zh.C04_WASHOUTS_INC_{i}]
§Y淘汰者§!支持度 §G+{j:.2f}%§!
[en.C04_WASHOUTS_DEC_{i}]
§YThe Washouts§!’ support §R-{j:.2f}%§!
[zh.C04_WASHOUTS_DEC_{i}]
§Y淘汰者§!支持度 §R-{j:.2f}%§!
[en.C04_WASHOUTS_GE_{i}]
§YThe Washouts§! has support no less than §Y{j:.2f}%§!
[zh.C04_WASHOUTS_GE_{i}]
§Y淘汰者§!支持度不低于 §Y{j:.2f}%§!
[en.C04_WASHOUTS_LE_{i}]
§YThe Washouts§! has support no more than §Y{j:.2f}%§!
[zh.C04_WASHOUTS_LE_{i}]
§Y淘汰者§!支持度不高于 §Y{j:.2f}%§!
"""

scripted_effects = dict()
with open("C04_POPULARITY.txt", "w", encoding='utf-8', errors='ignore') as f:
    for i in range(1, 1001):
        f.write(template.format(i=i,j=i/10) + "\n\n")
        scripted_effects |= {
            f"C04_ADD_SKY_STINGER_SUPPORT_{i}": {
                "set_variable": {
                    "var": "C04.VAR_DELTA",
                    "value": float(f"{i/10:.2f}"),
                },
                "MODIFY_C04_BY_ELECTION_SKY_STINGER_SUPPORT": True
            },
            f"C04_DEL_SKY_STINGER_SUPPORT_{i}": {
                "set_variable": {
                    "var": "C04.VAR_DELTA",
                    "value": float(f"{-i/10:.2f}"),
                },
                "MODIFY_C04_BY_ELECTION_SKY_STINGER_SUPPORT": True
            },
            f"C04_ADD_WIND_RIDER_SUPPORT_{i}": {
                "set_variable": {
                    "var": "C04.VAR_DELTA",
                    "value": float(f"{i/10:.2f}"),
                },
                "MODIFY_C04_BY_ELECTION_WIND_RIDER_SUPPORT": True
            },
            f"C04_DEL_WIND_RIDER_SUPPORT_{i}": {
                "set_variable": {
                    "var": "C04.VAR_DELTA",
                    "value": float(f"{-i/10:.2f}"),
                },
                "MODIFY_C04_BY_ELECTION_WIND_RIDER_SUPPORT": True
            },
            f"C04_ADD_WASHOUTS_SUPPORT_{i}": {
                "set_variable": {
                    "var": "C04.VAR_DELTA",
                    "value": float(f"{i/10:.2f}"),
                },
                "MODIFY_C04_BY_ELECTION_WASHOUTS_SUPPORT": True
            },
            f"C04_DEL_WASHOUTS_SUPPORT_{i}": {
                "set_variable": {
                    "var": "C04.VAR_DELTA",
                    "value": float(f"{-i/10:.2f}"),
                },
                "MODIFY_C04_BY_ELECTION_WASHOUTS_SUPPORT": True
            }
        }
SaveJson(scripted_effects, "../copies/data/common/scripted_effects/PIHC_C04_BY_ELECTION_EXTRA.json", indent=4)
# %%
