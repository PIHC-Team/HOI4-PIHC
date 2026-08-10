from hoi4dev import *

STRATUS_STATE_GROUPS = {
    "STRATUS_STRATUSBURG": [336, 37],
    "STRATUS_TIMBUCKTU": [376],
    "STRATUS_WEATHER_LAB": [46, 360],
    "STRATUS_WONDERBOLTS": [388],
    "STRATUS_WEATHER_FACTORY": [365],
    "STRATUS_RAINBOW_FACTORY": [364],
    "STRATUS_CLOUDSDALE": [400, 410, 412, 426, 441, 446, 436],
    "STRATUS_VANHOOVER": [355, 409, 52, 418, 386],
}
STRATUS_ID_MAPPING = {
    "STRATUS_STRATUSBURG": 1,
    "STRATUS_TIMBUCKTU": 2,
    "STRATUS_WEATHER_LAB": 3,
    "STRATUS_WONDERBOLTS": 4,
    "STRATUS_WEATHER_FACTORY": 5,
    "STRATUS_RAINBOW_FACTORY": 6,
    "STRATUS_CLOUDSDALE": 7,
    "STRATUS_VANHOOVER": 8,
}

def add_stratusburg_state_group_gui():
    workspace_path = "./scripts/region_gui/stratus/"
    CreateFolder(workspace_path)
    BatchCreateStateGroupImages(named_state_groups=STRATUS_STATE_GROUPS, output_path=workspace_path,
        internal_color = (248,234,98),
        border_color = (218,204,68),
        internal_highlight = (255,255,128),
        border_highlight = (248,234,98),
        processing = True,
        alpha = 0.8,
    )
    gfxs_path = "./resources/copies/gfx/interface/state_group_guis/"
    interface_path = "./resources/copies/data/interface/"
    sprites = dict()
    for group_name in STRATUS_STATE_GROUPS:
        img = ImageLoad(pjoin(workspace_path, f"highlighted_imgs/{group_name}.png"))
        ImageSave(img, pjoin(gfxs_path, f"{group_name}.dds"), compression='no')
        sprites = merge_dicts([sprites, {
            "spriteType": {
                "name": f"GFX_state_group_gui_STRATUS_{STRATUS_ID_MAPPING[group_name]}",
                "textureFile": f"gfx/interface/state_group_guis/{group_name}.dds",
                "noOfFrames": 2,
                "transparencecheck": True
            }
        }], d=True)
    SaveJson({'spriteTypes': sprites}, pjoin(interface_path, "PIHC_C04_state_group_gui_gfx.json"), indent=4)
    SaveJson({
        'guiTypes': {
            "containerWindowType": {
                "name": "C04_state_group_gui_entry_container",
                "buttonType": {
                    "name": "state_group_btn",
                    "spriteType": "GFX_state_group_gui_STRATUS_1",
                    "pdx_tooltip": "C04_state_group_btn_tooltip",
                    "scale": 0.75
                }
            }
        }
    }, pjoin(interface_path, "PIHC_C04_state_group_gui.json"), indent=4)


def add_stratusburg_state_group_update_effects():
    info = dict()
    with open("./resources/locs/C04_modifications.txt", "w") as f:
        for r in "012345678":
            for o in ["ADD", "DEL"]:
                for p in list(range(1,25)) + list(range(25, 105, 5)) + [200]:
                    key = f"C04_{o}_ECO_{r}_{p}"; v = 1+p/100 if o=="ADD" else 1-p/100
                    info[key] = {
                        "custom_effect_tooltip": f"{key}_TOOLTIP",
                    }
                    rs = [int(r)] if r!='0' else [1,2,3,4,5,6,7,8]
                    var = "C04.ARRAY_REGIONAL_DEV_REGIONS_ECONOMIC_FACTOR"
                    for r_ in rs:
                        info[key] = merge_dicts([info[key], { "multiply_variable": { var+f"^{r_-1}" : float(f"{v:.2f}") } }, {
                            "clamp_variable": {
                                "var": var+f"^{r_-1}",
                                "min": 0.000,
                                "max": 100.0
                            },
                        }], d=True)
                    info[key] = merge_dicts([info[key], {"C04_REGIONAL_DEV_COMPUTE": True}], d=True)
                    locs = f"""[zh.{key}_TOOLTIP]
§C{'全国' if r=='0' else '$C04_REGIONAL_DEV_STATE_GROUP_'+r+'$'}§!的§Y经济积极度§!§{'R-' if o=='DEL' else 'G+'}{p:.1f}%§!（相对值）。
[en.{key}_TOOLTIP]
The §C{'nation' if r=='0' else '$C04_REGIONAL_DEV_STATE_GROUP_'+r+'$'}§!’s §YEconomic Activity§! §{'R-' if o=='DEL' else 'G+'}{p:.1f}%§! (relative value).
"""
                    f.write(locs + "\n")
    SaveJson(info, "./resources/copies/data/common/scripted_effects/PIHC_C04_MODIFICATIONS.json", indent=4)

if __name__=="__main__":
    add_stratusburg_state_group_gui()
    add_stratusburg_state_group_update_effects()