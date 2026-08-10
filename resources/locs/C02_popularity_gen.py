# %%
from pyheaven import *

template = """
[en.C02_TRIXIE_LULAMOON_INC_{i}]
§YTrixie Lulamoon§!’s support §G+{i:.2f}%§!
[zh.C02_TRIXIE_LULAMOON_INC_{i}]
§Y特丽克西·卢拉月§!支持度 §G+{i:.2f}%§!
[en.C02_TRIXIE_LULAMOON_DEC_{i}]
§YTrixie Lulamoon§!’s support §R-{i:.2f}%§!
[zh.C02_TRIXIE_LULAMOON_DEC_{i}]
§Y特丽克西·卢拉月§!支持度 §R-{i:.2f}%§!
[en.C02_TRIXIE_LULAMOON_GE_{i}]
§YTrixie Lulamoon§! has support no less than §Y{i:.2f}%§!
[zh.C02_TRIXIE_LULAMOON_GE_{i}]
§Y特丽克西·卢拉月§!支持度不低于 §Y{i:.2f}%§!
[en.C02_TRIXIE_LULAMOON_LE_{i}]
§YTrixie Lulamoon§! has support no more than §Y{i:.2f}%§!
[zh.C02_TRIXIE_LULAMOON_LE_{i}]
§Y特丽克西·卢拉月§!支持度不高于 §Y{i:.2f}%§!

[en.C02_MARE_INC_{i}]
§YMare§!’s support §G+{i:.2f}%§!
[zh.C02_MARE_INC_{i}]
§Y梅耶§!支持度 §G+{i:.2f}%§!
[en.C02_MARE_DEC_{i}]
§YMare§!’s support §R-{i:.2f}%§!
[zh.C02_MARE_DEC_{i}]
§Y梅耶§!支持度 §R-{i:.2f}%§!
[en.C02_MARE_GE_{i}]
§YMare§! has support no less than §Y{i:.2f}%§!
[zh.C02_MARE_GE_{i}]
§Y梅耶§!支持度不低于 §Y{i:.2f}%§!
[en.C02_MARE_LE_{i}]
§YMare§! has support no more than §Y{i:.2f}%§!
[zh.C02_MARE_LE_{i}]
§Y梅耶§!支持度不高于 §Y{i:.2f}%§!

[en.C02_OCTAVIA_INC_{i}]
§YOctavia§!’s support §G+{i:.2f}%§!
[zh.C02_OCTAVIA_INC_{i}]
§Y奥塔薇娅§!支持度 §G+{i:.2f}%§!
[en.C02_OCTAVIA_DEC_{i}]
§YOctavia§!’s support §R-{i:.2f}%§!
[zh.C02_OCTAVIA_DEC_{i}]
§Y奥塔薇娅§!支持度 §R-{i:.2f}%§!
[en.C02_OCTAVIA_GE_{i}]
§YOctavia§! has support no less than §Y{i:.2f}%§!
[zh.C02_OCTAVIA_GE_{i}]
§Y奥塔薇娅§!支持度不低于 §Y{i:.2f}%§!
[en.C02_OCTAVIA_LE_{i}]
§YOctavia§! has support no more than §Y{i:.2f}%§!
[zh.C02_OCTAVIA_LE_{i}]
§Y奥塔薇娅§!支持度不高于 §Y{i:.2f}%§!

[en.C02_FILTHY_RICH_INC_{i}]
§YFilthy Rich§!’s support §G+{i:.2f}%§!
[zh.C02_FILTHY_RICH_INC_{i}]
§Y钱多多§!支持度 §G+{i:.2f}%§!
[en.C02_FILTHY_RICH_DEC_{i}]
§YFilthy Rich§!’s support §R-{i:.2f}%§!
[zh.C02_FILTHY_RICH_DEC_{i}]
§Y钱多多§!支持度 §R-{i:.2f}%§!
[en.C02_FILTHY_RICH_GE_{i}]
§YFilthy Rich§! has support no less than §Y{i:.2f}%§!
[zh.C02_FILTHY_RICH_GE_{i}]
§Y钱多多§!支持度不低于 §Y{i:.2f}%§!
[en.C02_FILTHY_RICH_LE_{i}]
§YFilthy Rich§! has support no more than §Y{i:.2f}%§!
[zh.C02_FILTHY_RICH_LE_{i}]
§Y钱多多§!支持度不高于 §Y{i:.2f}%§!

[en.C02_DOCTOR_HOOVES_INC_{i}]
§YDr. Hooves’ Support §G+{i:.2f}%§!
[zh.C02_DOCTOR_HOOVES_INC_{i}]
§Y蹄博士§!支持度 §G+{i:.2f}%§!
[en.C02_DOCTOR_HOOVES_DEC_{i}]
§YDr. Hooves’ Support §R-{i:.2f}%§!
[zh.C02_DOCTOR_HOOVES_DEC_{i}]
§Y蹄博士§!支持度 §R-{i:.2f}%§!
[en.C02_DOCTOR_HOOVES_GE_{i}]
§YDr. Hooves’ Support no less than §Y{i:.2f}%§!
[zh.C02_DOCTOR_HOOVES_GE_{i}]
§Y蹄博士§!支持度不低于 §Y{i:.2f}%§!
[en.C02_DOCTOR_HOOVES_LE_{i}]
§YDr. Hooves’ Support no more than §Y{i:.2f}%§!
[zh.C02_DOCTOR_HOOVES_LE_{i}]
§Y蹄博士§!支持度不高于 §Y{i:.2f}%§!

[en.C02_CRACKLE_COSETTE_INC_{i}]
§YCrackle Cosette§!’s support §G+{i:.2f}%§!
[zh.C02_CRACKLE_COSETTE_INC_{i}]
§Y爆裂甜菜§!支持度 §G+{i:.2f}%§!
[en.C02_CRACKLE_COSETTE_DEC_{i}]
§YCrackle Cosette§!’s support §R-{i:.2f}%§!
[zh.C02_CRACKLE_COSETTE_DEC_{i}]
§Y爆裂甜菜§!支持度 §R-{i:.2f}%§!
[en.C02_CRACKLE_COSETTE_GE_{i}]
§YCrackle Cosette§! has support no less than §Y{i:.2f}%§!
[zh.C02_CRACKLE_COSETTE_GE_{i}]
§Y爆裂甜菜§!支持度不低于 §Y{i:.2f}%§!
[en.C02_CRACKLE_COSETTE_LE_{i}]
§YCrackle Cosette§! has support no more than §Y{i:.2f}%§!
[zh.C02_CRACKLE_COSETTE_LE_{i}]
§Y爆裂甜菜§!支持度不高于 §Y{i:.2f}%§!
"""

with open("C02_POPULARITY.txt", "w", encoding='utf-8', errors='ignore') as f:
    for i in range(1, 101):
        f.write(template.format(i=i) + "\n\n")

# %%
