# %%
from hoi4dev import *

images = [file for file in ListFiles("__img__") if file.endswith(".png")]
for i, image_file in enumerate(sorted(images)):
    CreateFolder(Prefix(image_file))
    idx, zh, en = Prefix(image_file).split("-",2)
    tag = en.replace(' ','_').replace("-","_").replace("'","").replace("’","").upper()
    SaveJson({
        "options": [
            {
                "ai_chance": {"factor": 100},
                f"ADD_INVENTORY_ITEM_5LG_ARTIFACT_{tag}_1": True,
                "add_tech_bonus": {
                    "bonus": 0.15,
                    "uses": 1,
                    "category": "pihc_magical",
                },
                "add_ideas": f"IDEA_ALL_ARTIFACT_{tag}",
                "hidden_effect": {
                    "if": {
                        "limit": {
                            "NOT": {
                                "has_tech": "TECHNOLOGY_TECH_MAGI_II",
                            },
                        },
                        "add_nuclear_bombs": 1,
                    },
                },
            }
        ],
        "fire_only_once": (idx not in ['001', '002', '004', '005', '020']),
        "mean_time_to_happen": {
            "years": 35,
            "modifier": {
                "factor": 0.5,
                "has_tech": "TECHNOLOGY_TECH_MAGI_DARKPERCEPTION",
            },
            "modifier__D1": {
                "factor": 0.5,
                "has_tech": "TECHNOLOGY_TECH_MAGI_II",
            },
            "modifier__D2": {
                "factor": 0.85,
                "has_idea_with_trait": "TRAIT_ARCHAEOLOGIST",
            },
            "modifier__D3": {
                "factor": 0.6,
                "has_idea_with_trait": "TRAIT_FANTASY_LITERATURE",
            },
        } | ({
            # Staff of Sacanas for everypony
            "modifier__D4": {
                "factor": 2.0,
                "always": True,
            }
        } if idx=='001' else {}) | ({
            # Alicorn Amulet for Trixie Lulamoon
            "modifier__D4": {
                "factor": 0.06,
                "tag": "C02",
            },
            "modifier__D5": {
                "factor": 5.0,
                "NOT": {
                    "tag": "C02"
                }
            },
            "modifier__D6": {
                "factor": 0.1,
                "tag": "C02",
                "date > 1004.06.01": None
            }
        } if idx=='009' else {}) | ({
            # Sonic Screwdriver for Doctor Hooves
            "modifier__D4": {
                "factor": 0.1,
                "has_idea": "CHARACTER_DOCTOR_HOOVES",
            }
        } if idx=='018' else {})
    }, pjoin(Prefix(image_file), "info.json"), indent=4)
    with open(pjoin(Prefix(image_file), "locs.txt"), "w", encoding='utf-8', errors='ignore') as f:
        f.write(
f"""[zh.@]
发现法器：{zh}
[en.@]
Discovered artifact: {en}
[zh.@desc]
近日一支考察队发现了失落已久的法器：{zh}！
[en.@desc]
Recently, an expedition team discovered a long-lost artifact: {en}!
[zh.@o0]
好吧
[en.@o0]
Okay
"""
        )
    CopyFile(pjoin("__img__",image_file), pjoin(Prefix(image_file), "default.png"), rm=True)
    
    CreateFolder(f"../../ideas/ALL_ARTIFACT_{tag}")
    CopyFile(pjoin(Prefix(image_file), "locs.txt"), f"../../ideas/ALL_ARTIFACT_{tag}/locs.txt", rm=True)
    SaveJson({
        "category": "hidden_ideas",
        "name": f"Artifact {en}",
        "removal_cost": -1,
        "modifier": {
            "country_resource_crystals": 1
        }
    }, f"../../ideas/ALL_ARTIFACT_{tag}/info.json", indent=4)

# %%