# %%
from hoi4dev import *

images = [file for file in ListFiles("__img__") if file.endswith(".png")]
for i, image_file in enumerate(sorted(images)):
    CreateFolder(Prefix(image_file))
    idx, zh, en = Prefix(image_file).split("-")
    tag = en.replace(' ','_').upper()
    SaveJson({
        "options": [
            {
                "ai_chance": {"factor": 100},
                "set_country_flag": f"PIHC_COUNTRY_FLAG_{tag}",
                "add_stability": -0.01,
                "add_manpower": -50,
            }
        ],
        "mean_time_to_happen": {
            "years": 10
        },
    }, pjoin(Prefix(image_file), "info.json"), indent=4)
    with open(pjoin(Prefix(image_file), "locs.txt"), "w", encoding='utf-8', errors='ignore') as f:
        f.write(
f"""[zh.@]
{zh}出没
[en.@]
{en} Appeared
[zh.@desc]
{zh}领地的生态环境破坏导致{zh}的活动加剧了，现在他们会在小马利亚的各个地方出没！
[en.@desc]
The ecological environment of {en} has been destroyed, which has intensified the activities of {en}. Now they will appear everywhere in Equestria!
[zh.@o0]
好吧
[en.@o0]
Okay
"""
        )
    CopyFile(pjoin("__img__",image_file), pjoin(Prefix(image_file), "default.png"))

# %%