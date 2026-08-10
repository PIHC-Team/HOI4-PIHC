# %%
from pyheaven import *

civ_template = """[zh.CUSTOM_COST_CIV_FACTORY_{i}]
£civ_factory §Y{i}§!
[en.CUSTOM_COST_CIV_FACTORY_{i}]
£civ_factory §Y{i}§!
[zh.CUSTOM_COST_CIV_FACTORY_{i}_blocked]
£civ_factory §R{i}§!
[en.CUSTOM_COST_CIV_FACTORY_{i}_blocked]
£civ_factory §R{i}§!
[zh.CUSTOM_COST_CIV_FACTORY_{i}_tooltip]
决议生效时将持续占用£civ_factory §Y{i}§!
[en.CUSTOM_COST_CIV_FACTORY_{i}_tooltip]
It costs £civ_factory §Y{i}§! while this decision is active
"""

civ_pp_template = """[zh.CUSTOM_COST_CIV_FACTORY_{i}_PP_{j}]
£civ_factory §Y{i}§! £pol_power §Y{j}§!
[en.CUSTOM_COST_CIV_FACTORY_{i}_PP_{j}]
£civ_factory §Y{i}§! £pol_power §Y{j}§!
[zh.CUSTOM_COST_CIV_FACTORY_{i}_PP_{j}_blocked]
£civ_factory §R{i}§! £pol_power §R{j}§!
[en.CUSTOM_COST_CIV_FACTORY_{i}_PP_{j}_blocked]
£civ_factory §R{i}§! £pol_power §R{j}§!
[zh.CUSTOM_COST_CIV_FACTORY_{i}_PP_{j}_tooltip]
决议消耗£pol_power §Y{j}§!启动，决议生效时将持续占用£civ_factory §Y{i}§!
[en.CUSTOM_COST_CIV_FACTORY_{i}_PP_{j}_tooltip]
It costs £pol_power §Y{j}§! to activate, and costs £civ_factory §Y{i}§! while this decision is active
"""

resources_template = """[zh.CUSTOM_COST_OIL_{i}]
£resources_strip|1 §Y{i}§!
[en.CUSTOM_COST_OIL_{i}]
£resources_strip|1 §Y{i}§!
[zh.CUSTOM_COST_OIL_{i}_blocked]
£resources_strip|1 §R{i}§!
[en.CUSTOM_COST_OIL_{i}_blocked]
£resources_strip|1 §R{i}§!
[zh.CUSTOM_COST_OIL_{i}_tooltip]
决议生效时将持续占用£resources_strip|1 §Y{i}§!
[en.CUSTOM_COST_OIL_{i}_tooltip]
It costs £resources_strip|1 §Y{i}§! while this decision is active
[zh.CUSTOM_COST_ALU_{i}]
£resources_strip|2 §Y{i}§!
[en.CUSTOM_COST_ALU_{i}]
£resources_strip|2 §Y{i}§!
[zh.CUSTOM_COST_ALU_{i}_blocked]
£resources_strip|2 §R{i}§!
[en.CUSTOM_COST_ALU_{i}_blocked]
£resources_strip|2 §R{i}§!
[zh.CUSTOM_COST_ALU_{i}_tooltip]
决议生效时将持续占用£resources_strip|2 §Y{i}§!
[en.CUSTOM_COST_ALU_{i}_tooltip]
It costs £resources_strip|2 §Y{i}§! while this decision is active
[zh.CUSTOM_COST_RUB_{i}]
£resources_strip|3 §Y{i}§!
[en.CUSTOM_COST_RUB_{i}]
£resources_strip|3 §Y{i}§!
[zh.CUSTOM_COST_RUB_{i}_blocked]
£resources_strip|3 §R{i}§!
[en.CUSTOM_COST_RUB_{i}_blocked]
£resources_strip|3 §R{i}§!
[zh.CUSTOM_COST_RUB_{i}_tooltip]
决议生效时将持续占用£resources_strip|3 §Y{i}§!
[en.CUSTOM_COST_RUB_{i}_tooltip]
It costs £resources_strip|3 §Y{i}§! while this decision is active
[zh.CUSTOM_COST_TUN_{i}]
£resources_strip|4 §Y{i}§!
[en.CUSTOM_COST_TUN_{i}]
£resources_strip|4 §Y{i}§!
[zh.CUSTOM_COST_TUN_{i}_blocked]
£resources_strip|4 §R{i}§!
[en.CUSTOM_COST_TUN_{i}_blocked]
£resources_strip|4 §R{i}§!
[zh.CUSTOM_COST_TUN_{i}_tooltip]
决议生效时将持续占用£resources_strip|4 §Y{i}§!
[en.CUSTOM_COST_TUN_{i}_tooltip]
It costs £resources_strip|4 §Y{i}§! while this decision is active
[zh.CUSTOM_COST_STE_{i}]
£resources_strip|5 §Y{i}§!
[en.CUSTOM_COST_STE_{i}]
£resources_strip|5 §Y{i}§!
[zh.CUSTOM_COST_STE_{i}_blocked]
£resources_strip|5 §R{i}§!
[en.CUSTOM_COST_STE_{i}_blocked]
£resources_strip|5 §R{i}§!
[zh.CUSTOM_COST_STE_{i}_tooltip]
决议生效时将持续占用£resources_strip|5 §Y{i}§!
[en.CUSTOM_COST_STE_{i}_tooltip]
It costs £resources_strip|5 §Y{i}§! while this decision is active
[zh.CUSTOM_COST_CHR_{i}]
£resources_strip|6 §Y{i}§!
[en.CUSTOM_COST_CHR_{i}]
£resources_strip|6 §Y{i}§!
[zh.CUSTOM_COST_CHR_{i}_blocked]
£resources_strip|6 §R{i}§!
[en.CUSTOM_COST_CHR_{i}_blocked]
£resources_strip|6 §R{i}§!
[zh.CUSTOM_COST_CHR_{i}_tooltip]
决议生效时将持续占用£resources_strip|6 §Y{i}§!
[en.CUSTOM_COST_CHR_{i}_tooltip]
It costs £resources_strip|6 §Y{i}§! while this decision is active
[zh.CUSTOM_COST_CRY_{i}]
£resources_strip|7 §Y{i}§!
[en.CUSTOM_COST_CRY_{i}]
£resources_strip|7 §Y{i}§!
[zh.CUSTOM_COST_CRY_{i}_blocked]
£resources_strip|7 §R{i}§!
[en.CUSTOM_COST_CRY_{i}_blocked]
£resources_strip|7 §R{i}§!
[zh.CUSTOM_COST_CRY_{i}_tooltip]
决议生效时将持续占用£resources_strip|7 §Y{i}§!
[en.CUSTOM_COST_CRY_{i}_tooltip]
It costs £resources_strip|7 §Y{i}§! while this decision is active
[zh.CUSTOM_COST_LOG_{i}]
£resources_strip|8 §Y{i}§!
[en.CUSTOM_COST_LOG_{i}]
£resources_strip|8 §Y{i}§!
[zh.CUSTOM_COST_LOG_{i}_blocked]
£resources_strip|8 §R{i}§!
[en.CUSTOM_COST_LOG_{i}_blocked]
£resources_strip|8 §R{i}§!
[zh.CUSTOM_COST_LOG_{i}_tooltip]
决议生效时将持续占用£resources_strip|8 §Y{i}§!
[en.CUSTOM_COST_LOG_{i}_tooltip]
It costs £resources_strip|8 §Y{i}§! while this decision is active
[zh.CUSTOM_COST_COA_{i}]
£resources_strip|9 §Y{i}§!
[en.CUSTOM_COST_COA_{i}]
£resources_strip|9 §Y{i}§!
[zh.CUSTOM_COST_COA_{i}_blocked]
£resources_strip|9 §R{i}§!
[en.CUSTOM_COST_COA_{i}_blocked]
£resources_strip|9 §R{i}§!
[zh.CUSTOM_COST_COA_{i}_tooltip]
决议生效时将持续占用£resources_strip|9 §Y{i}§!
[en.CUSTOM_COST_COA_{i}_tooltip]
It costs £resources_strip|9 §Y{i}§! while this decision is active
"""

resources_pp_template = """[zh.CUSTOM_COST_OIL_{i}_PP_{j}]
£resources_strip|1 §Y{i}§! £pol_power §Y{j}§!
[en.CUSTOM_COST_OIL_{i}_PP_{j}]
£resources_strip|1 §Y{i}§! £pol_power §Y{j}§!
[zh.CUSTOM_COST_OIL_{i}_PP_{j}_blocked]
£resources_strip|1 §R{i}§! £pol_power §R{j}§!
[en.CUSTOM_COST_OIL_{i}_PP_{j}_blocked]
£resources_strip|1 §R{i}§! £pol_power §R{j}§!
[zh.CUSTOM_COST_OIL_{i}_PP_{j}_tooltip]
决议消耗£pol_power §Y{j}§!启动，决议生效时将持续占用£resources_strip|1 §Y{i}§!
[en.CUSTOM_COST_OIL_{i}_PP_{j}_tooltip]
It costs £pol_power §Y{j}§! to activate, and costs £resources_strip|1 §Y{i}§! while this decision is active
[zh.CUSTOM_COST_ALU_{i}_PP_{j}]
£resources_strip|2 §Y{i}§! £pol_power §Y{j}§!
[en.CUSTOM_COST_ALU_{i}_PP_{j}]
£resources_strip|2 §Y{i}§! £pol_power §Y{j}§!
[zh.CUSTOM_COST_ALU_{i}_PP_{j}_blocked]
£resources_strip|2 §R{i}§! £pol_power §R{j}§!
[en.CUSTOM_COST_ALU_{i}_PP_{j}_blocked]
£resources_strip|2 §R{i}§! £pol_power §R{j}§!
[zh.CUSTOM_COST_ALU_{i}_PP_{j}_tooltip]
决议消耗£pol_power §Y{j}§!启动，决议生效时将持续占用£resources_strip|2 §Y{i}§!
[en.CUSTOM_COST_ALU_{i}_PP_{j}_tooltip]
It costs £pol_power §Y{j}§! to activate, and costs £resources_strip|2 §Y{i}§! while this decision is active
[zh.CUSTOM_COST_RUB_{i}_PP_{j}]
£resources_strip|3 §Y{i}§! £pol_power §Y{j}§!
[en.CUSTOM_COST_RUB_{i}_PP_{j}]
£resources_strip|3 §Y{i}§! £pol_power §Y{j}§!
[zh.CUSTOM_COST_RUB_{i}_PP_{j}_blocked]
£resources_strip|3 §R{i}§! £pol_power §R{j}§!
[en.CUSTOM_COST_RUB_{i}_PP_{j}_blocked]
£resources_strip|3 §R{i}§! £pol_power §R{j}§!
[zh.CUSTOM_COST_RUB_{i}_PP_{j}_tooltip]
决议消耗£pol_power §Y{j}§!启动，决议生效时将持续占用£resources_strip|3 §Y{i}§!
[en.CUSTOM_COST_RUB_{i}_PP_{j}_tooltip]
It costs £pol_power §Y{j}§! to activate, and costs £resources_strip|3 §Y{i}§! while this decision is active
[zh.CUSTOM_COST_TUN_{i}_PP_{j}]
£resources_strip|4 §Y{i}§! £pol_power §Y{j}§!
[en.CUSTOM_COST_TUN_{i}_PP_{j}]
£resources_strip|4 §Y{i}§! £pol_power §Y{j}§!
[zh.CUSTOM_COST_TUN_{i}_PP_{j}_blocked]
£resources_strip|4 §R{i}§! £pol_power §R{j}§!
[en.CUSTOM_COST_TUN_{i}_PP_{j}_blocked]
£resources_strip|4 §R{i}§! £pol_power §R{j}§!
[zh.CUSTOM_COST_TUN_{i}_PP_{j}_tooltip]
决议消耗£pol_power §Y{j}§!启动，决议生效时将持续占用£resources_strip|4 §Y{i}§!
[en.CUSTOM_COST_TUN_{i}_PP_{j}_tooltip]
It costs £pol_power §Y{j}§! to activate, and costs £resources_strip|4 §Y{i}§! while this decision is active
[zh.CUSTOM_COST_STE_{i}_PP_{j}]
£resources_strip|5 §Y{i}§! £pol_power §Y{j}§!
[en.CUSTOM_COST_STE_{i}_PP_{j}]
£resources_strip|5 §Y{i}§! £pol_power §Y{j}§!
[zh.CUSTOM_COST_STE_{i}_PP_{j}_blocked]
£resources_strip|5 §R{i}§! £pol_power §R{j}§!
[en.CUSTOM_COST_STE_{i}_PP_{j}_blocked]
£resources_strip|5 §R{i}§! £pol_power §R{j}§!
[zh.CUSTOM_COST_STE_{i}_PP_{j}_tooltip]
决议消耗£pol_power §Y{j}§!启动，决议生效时将持续占用£resources_strip|5 §Y{i}§!
[en.CUSTOM_COST_STE_{i}_PP_{j}_tooltip]
It costs £pol_power §Y{j}§! to activate, and costs £resources_strip|5 §Y{i}§! while this decision is active
[zh.CUSTOM_COST_CHR_{i}_PP_{j}]
£resources_strip|6 §Y{i}§! £pol_power §Y{j}§!
[en.CUSTOM_COST_CHR_{i}_PP_{j}]
£resources_strip|6 §Y{i}§! £pol_power §Y{j}§!
[zh.CUSTOM_COST_CHR_{i}_PP_{j}_blocked]
£resources_strip|6 §R{i}§! £pol_power §R{j}§!
[en.CUSTOM_COST_CHR_{i}_PP_{j}_blocked]
£resources_strip|6 §R{i}§! £pol_power §R{j}§!
[zh.CUSTOM_COST_CHR_{i}_PP_{j}_tooltip]
决议消耗£pol_power §Y{j}§!启动，决议生效时将持续占用£resources_strip|6 §Y{i}§!
[en.CUSTOM_COST_CHR_{i}_PP_{j}_tooltip]
It costs £pol_power §Y{j}§! to activate, and costs £resources_strip|6 §Y{i}§! while this decision is active
[zh.CUSTOM_COST_CRY_{i}_PP_{j}]
£resources_strip|7 §Y{i}§! £pol_power §Y{j}§!
[en.CUSTOM_COST_CRY_{i}_PP_{j}]
£resources_strip|7 §Y{i}§! £pol_power §Y{j}§!
[zh.CUSTOM_COST_CRY_{i}_PP_{j}_blocked]
£resources_strip|7 §R{i}§! £pol_power §R{j}§!
[en.CUSTOM_COST_CRY_{i}_PP_{j}_blocked]
£resources_strip|7 §R{i}§! £pol_power §R{j}§!
[zh.CUSTOM_COST_CRY_{i}_PP_{j}_tooltip]
决议消耗£pol_power §Y{j}§!启动，决议生效时将持续占用£resources_strip|7 §Y{i}§!
[en.CUSTOM_COST_CRY_{i}_PP_{j}_tooltip]
It costs £pol_power §Y{j}§! to activate, and costs £resources_strip|7 §Y{i}§! while this decision is active
[zh.CUSTOM_COST_LOG_{i}_PP_{j}]
£resources_strip|8 §Y{i}§! £pol_power §Y{j}§!
[en.CUSTOM_COST_LOG_{i}_PP_{j}]
£resources_strip|8 §Y{i}§! £pol_power §Y{j}§!
[zh.CUSTOM_COST_LOG_{i}_PP_{j}_blocked]
£resources_strip|8 §R{i}§! £pol_power §R{j}§!
[en.CUSTOM_COST_LOG_{i}_PP_{j}_blocked]
£resources_strip|8 §R{i}§! £pol_power §R{j}§!
[zh.CUSTOM_COST_LOG_{i}_PP_{j}_tooltip]
决议消耗£pol_power §Y{j}§!启动，决议生效时将持续占用£resources_strip|8 §Y{i}§!
[en.CUSTOM_COST_LOG_{i}_PP_{j}_tooltip]
It costs £pol_power §Y{j}§! to activate, and costs £resources_strip|8 §Y{i}§! while this decision is active
[zh.CUSTOM_COST_COA_{i}_PP_{j}]
£resources_strip|9 §Y{i}§! £pol_power §Y{j}§!
[en.CUSTOM_COST_COA_{i}_PP_{j}]
£resources_strip|9 §Y{i}§! £pol_power §Y{j}§!
[zh.CUSTOM_COST_COA_{i}_PP_{j}_blocked]
£resources_strip|9 §R{i}§! £pol_power §R{j}§!
[en.CUSTOM_COST_COA_{i}_PP_{j}_blocked]
£resources_strip|9 §R{i}§! £pol_power §R{j}§!
[zh.CUSTOM_COST_COA_{i}_PP_{j}_tooltip]
决议消耗£pol_power §Y{j}§!启动，决议生效时将持续占用£resources_strip|9 §Y{i}§!
[en.CUSTOM_COST_COA_{i}_PP_{j}_tooltip]
It costs £pol_power §Y{j}§! to activate, and costs £resources_strip|9 §Y{i}§! while this decision is active
"""

with open("custom_cost.txt", "w", encoding='utf-8', errors='ignore') as f:
    for i in range(1, 26):
        f.write(civ_template.format(i=i) + "\n\n")
    for i in range(1, 26):
        for j in range(5, 305, 5):
            f.write(civ_pp_template.format(i=i, j=j) + "\n\n")
    for i in range(1, 26):
        f.write(resources_template.format(i=i) + "\n\n")
    for i in range(1, 26):
        for j in range(5, 305, 5):
            f.write(resources_pp_template.format(i=i, j=j) + "\n\n")

# %%
WETM_template = """[zh.CUSTOM_COST_ZAP_APPLES_{c}]
£wetm_zap §Y{c}§!
[en.CUSTOM_COST_ZAP_APPLES_{c}]
£wetm_zap §Y{c}§!
[zh.CUSTOM_COST_ZAP_APPLES_{c}_blocked]
£wetm_zap §R{c}§!
[en.CUSTOM_COST_ZAP_APPLES_{c}_blocked]
£wetm_zap §R{c}§!
[zh.CUSTOM_COST_ZAP_APPLES_{c}_tooltip]
消耗§Y{c}§!个$WETM_ZAP_APPLES$
[en.CUSTOM_COST_ZAP_APPLES_{c}_tooltip]
Costs §Y{c}§! $WETM_ZAP_APPLES$

[zh.CUSTOM_COST_ORE_BOULDERS_{c}]
£wetm_boulder §Y{c}§!
[en.CUSTOM_COST_ORE_BOULDERS_{c}]
£wetm_boulder §Y{c}§!
[zh.CUSTOM_COST_ORE_BOULDERS_{c}_blocked]
£wetm_boulder §R{c}§!
[en.CUSTOM_COST_ORE_BOULDERS_{c}_blocked]
£wetm_boulder §R{c}§!
[zh.CUSTOM_COST_ORE_BOULDERS_{c}_tooltip]
消耗§Y{c}§!个$WETM_ORE_BOULDERS$
[en.CUSTOM_COST_ORE_BOULDERS_{c}_tooltip]
Costs §Y{c}§! $WETM_ORE_BOULDERS$

[zh.CUSTOM_COST_BLUEPRINTS_{c}]
£wetm_blueprint §Y{c}§!
[en.CUSTOM_COST_BLUEPRINTS_{c}]
£wetm_blueprint §Y{c}§!
[zh.CUSTOM_COST_BLUEPRINTS_{c}_blocked]
£wetm_blueprint §R{c}§!
[en.CUSTOM_COST_BLUEPRINTS_{c}_blocked]
£wetm_blueprint §R{c}§!
[zh.CUSTOM_COST_BLUEPRINTS_{c}_tooltip]
消耗§Y{c}§!个$WETM_BLUEPRINTS$
[en.CUSTOM_COST_BLUEPRINTS_{c}_tooltip]
Costs §Y{c}§! $WETM_BLUEPRINTS$

[zh.CUSTOM_COST_DEV_BONDS_{c}]
£wetm_bond §Y{c}§!
[en.CUSTOM_COST_DEV_BONDS_{c}]
£wetm_bond §Y{c}§!
[zh.CUSTOM_COST_DEV_BONDS_{c}_blocked]
£wetm_bond §R{c}§!
[en.CUSTOM_COST_DEV_BONDS_{c}_blocked]
£wetm_bond §R{c}§!
[zh.CUSTOM_COST_DEV_BONDS_{c}_tooltip]
消耗§Y{c}§!个$WETM_DEV_BONDS$
[en.CUSTOM_COST_DEV_BONDS_{c}_tooltip]
Costs §Y{c}§! $WETM_DEV_BONDS$
"""

with open("WETM_custom_cost.txt", "w", encoding='utf-8', errors='ignore') as f:
    for c in range(100, 2500, 100):
        f.write(WETM_template.format(c=c) + "\n\n")

# %%
WETM_gain_template = """[zh.CUSTOM_GAIN_ZAP_APPLES_{c}]
获得 §Y{c}§! 个 $WETM_ZAP_APPLES$
[en.CUSTOM_GAIN_ZAP_APPLES_{c}]
Gain §Y{c}§! $WETM_ZAP_APPLES$

[zh.CUSTOM_GAIN_ORE_BOULDERS_{c}]
获得 §Y{c}§! 个 $WETM_ORE_BOULDERS$
[en.CUSTOM_GAIN_ORE_BOULDERS_{c}]
Gain §Y{c}§! $WETM_ORE_BOULDERS$

[zh.CUSTOM_GAIN_BLUEPRINTS_{c}]
获得 §Y{c}§! 个 $WETM_BLUEPRINTS$
[en.CUSTOM_GAIN_BLUEPRINTS_{c}]
Gain §Y{c}§! $WETM_BLUEPRINTS$

[zh.CUSTOM_GAIN_DEV_BONDS_{c}]
获得 §Y{c}§! 个 $WETM_DEV_BONDS$
[en.CUSTOM_GAIN_DEV_BONDS_{c}]
Gain §Y{c}§! $WETM_DEV_BONDS$
"""

with open("WETM_custom_gain.txt", "w", encoding='utf-8', errors='ignore') as f:
    for c in range(100, 2500, 100):
        f.write(WETM_gain_template.format(c=c) + "\n\n")

# %%
WETM_spend_template = """[zh.CUSTOM_SPEND_ZAP_APPLES_{c}]
消耗 §Y{c}§! 个 $WETM_ZAP_APPLES$
[en.CUSTOM_SPEND_ZAP_APPLES_{c}]
Spend §Y{c}§! $WETM_ZAP_APPLES$

[zh.CUSTOM_SPEND_ORE_BOULDERS_{c}]
消耗 §Y{c}§! 个 $WETM_ORE_BOULDERS$
[en.CUSTOM_SPEND_ORE_BOULDERS_{c}]
Spend §Y{c}§! $WETM_ORE_BOULDERS$

[zh.CUSTOM_SPEND_BLUEPRINTS_{c}]
消耗 §Y{c}§! 个 $WETM_BLUEPRINTS$
[en.CUSTOM_SPEND_BLUEPRINTS_{c}]
Spend §Y{c}§! $WETM_BLUEPRINTS$

[zh.CUSTOM_SPEND_DEV_BONDS_{c}]
消耗 §Y{c}§! 个 $WETM_DEV_BONDS$
[en.CUSTOM_SPEND_DEV_BONDS_{c}]
Spend §Y{c}§! $WETM_DEV_BONDS$
"""

with open("WETM_custom_spend.txt", "w", encoding='utf-8', errors='ignore') as f:
    for c in range(100, 2500, 100):
        f.write(WETM_spend_template.format(c=c) + "\n\n")

# %%
WETM_own_template = """[zh.CUSTOM_OWN_ZAP_APPLES_{c}]
拥有不少于 §Y{c}§! 个 $WETM_ZAP_APPLES$
[en.CUSTOM_OWN_ZAP_APPLES_{c}]
Own at least §Y{c}§! $WETM_ZAP_APPLES$

[zh.CUSTOM_OWN_ORE_BOULDERS_{c}]
拥有不少于 §Y{c}§! 个 $WETM_ORE_BOULDERS$
[en.CUSTOM_OWN_ORE_BOULDERS_{c}]
Own at least §Y{c}§! $WETM_ORE_BOULDERS$

[zh.CUSTOM_OWN_BLUEPRINTS_{c}]
拥有不少于 §Y{c}§! 个 $WETM_BLUEPRINTS$
[en.CUSTOM_OWN_BLUEPRINTS_{c}]
Own at least §Y{c}§! $WETM_BLUEPRINTS$

[zh.CUSTOM_OWN_DEV_BONDS_{c}]
拥有不少于 §Y{c}§! 个 $WETM_DEV_BONDS$
[en.CUSTOM_OWN_DEV_BONDS_{c}]
Own at least §Y{c}§! $WETM_DEV_BONDS$
"""

with open("WETM_custom_own.txt", "w", encoding='utf-8', errors='ignore') as f:
    for c in range(100, 2500, 100):
        f.write(WETM_own_template.format(c=c) + "\n\n")

# %%
C03_muffins_template = """
[zh.CUSTOM_COST_MUFFINS_{c}]
£muffins §Y{c}§!
[en.CUSTOM_COST_MUFFINS_{c}]
£muffins §Y{c}§!
[zh.CUSTOM_COST_MUFFINS_{c}_blocked]
£muffins §R{c}§!
[en.CUSTOM_COST_MUFFINS_{c}_blocked]
£muffins §R{c}§!
[zh.CUSTOM_COST_MUFFINS_{c}_tooltip]
消耗§Y{c}§!个$C03_MUFFINS$
[en.CUSTOM_COST_MUFFINS_{c}_tooltip]
Costs §Y{c}§! $C03_MUFFINS$

[zh.CUSTOM_GAIN_MUFFINS_{c}]
获得 §Y{c}§! 个 $C03_MUFFINS$
[en.CUSTOM_GAIN_MUFFINS_{c}]
Gain §Y{c}§! $C03_MUFFINS$

[zh.CUSTOM_SPEND_MUFFINS_{c}]
消耗 §Y{c}§! 个 $C03_MUFFINS$
[en.CUSTOM_SPEND_MUFFINS_{c}]
Spend §Y{c}§! $C03_MUFFINS$

[zh.CUSTOM_OWN_MUFFINS_{c}]
拥有不少于 §Y{c}§! 个 $C03_MUFFINS$
[en.CUSTOM_OWN_MUFFINS_{c}]
Own at least §Y{c}§! $C03_MUFFINS$
"""

C03_muffins_pp_template = """
[zh.CUSTOM_COST_MUFFINS_{c}_PP_{j}]
£muffins §Y{c}§! £pol_power §Y{j}§!
[en.CUSTOM_COST_MUFFINS_{c}_PP_{j}]
£muffins §Y{c}§! £pol_power §Y{j}§!
[zh.CUSTOM_COST_MUFFINS_{c}_PP_{j}_blocked]
£muffins §R{c}§! £pol_power §R{j}§!
[en.CUSTOM_COST_MUFFINS_{c}_PP_{j}_blocked]
£muffins §R{c}§! £pol_power §R{j}§!
[zh.CUSTOM_COST_MUFFINS_{c}_PP_{j}_tooltip]
消耗§Y{c}§!个$C03_MUFFINS$ 和 £pol_power §Y{j}§!
[en.CUSTOM_COST_MUFFINS_{c}_PP_{j}_tooltip]
Costs §Y{c}§! $C03_MUFFINS$ and £pol_power §Y{j}§!
"""

with open("C03_muffins_batch.txt", "w", encoding='utf-8', errors='ignore') as f:
    for c in list(range(0,10)) + list(range(10,100,5)) + list(range(100, 1000, 50)) + list(range(1000, 10000, 500)) + [200000, 1000000]:
        f.write(C03_muffins_template.format(c=c) + "\n\n")
        for j in range(5, 305, 5):
            f.write(C03_muffins_pp_template.format(c=c, j=j) + "\n\n")

# %%
C18_cure_template = """
[zh.CUSTOM_COST_CURE_{c}]
£foals_breath §Y{c}§!
[en.CUSTOM_COST_CURE_{c}]
£foals_breath §Y{c}§!
[zh.CUSTOM_COST_CURE_{c}_blocked]
£foals_breath §R{c}§!
[en.CUSTOM_COST_CURE_{c}_blocked]
£foals_breath §R{c}§!
[zh.CUSTOM_COST_CURE_{c}_tooltip]
消耗§Y{c}§!份$C18_CURE$
[en.CUSTOM_COST_CURE_{c}_tooltip]
Costs §Y{c}§! $C18_CURE$

[zh.CUSTOM_GAIN_CURE_{c}]
获得 §Y{c}§! 份 $C18_CURE$
[en.CUSTOM_GAIN_CURE_{c}]
Gain §Y{c}§! $C18_CURE$

[zh.CUSTOM_SPEND_CURE_{c}]
消耗 §Y{c}§! 份 $C18_CURE$
[en.CUSTOM_SPEND_CURE_{c}]
Spend §Y{c}§! $C18_CURE$

[zh.CUSTOM_OWN_CURE_{c}]
拥有不少于 §Y{c}§! 份 $C18_CURE$
[en.CUSTOM_OWN_CURE_{c}]
Own at least §Y{c}§! $C18_CURE$
"""

C18_cure_pp_template = """
[zh.CUSTOM_COST_CURE_{c}_PP_{j}]
£foals_breath §Y{c}§! £pol_power §Y{j}§!
[en.CUSTOM_COST_CURE_{c}_PP_{j}]
£foals_breath §Y{c}§! £pol_power §Y{j}§!
[zh.CUSTOM_COST_CURE_{c}_PP_{j}_blocked]
£foals_breath §R{c}§! £pol_power §R{j}§!
[en.CUSTOM_COST_CURE_{c}_PP_{j}_blocked]
£foals_breath §R{c}§! £pol_power §R{j}§!
[zh.CUSTOM_COST_CURE_{c}_PP_{j}_tooltip]
消耗§Y{c}§!份$C18_CURE$ 和 £pol_power §Y{j}§!
[en.CUSTOM_COST_CURE_{c}_PP_{j}_tooltip]
Costs §Y{c}§! $C18_CURE$ and £pol_power §Y{j}§!
"""

with open("C18_cure_batch.txt", "w", encoding='utf-8', errors='ignore') as f:
    for c in list(range(0,10)) + list(range(10,100,5)) + list(range(100, 1000, 50)) + list(range(1000, 10000, 500)) + [200000, 1000000]:
        f.write(C18_cure_template.format(c=c) + "\n\n")
        for j in range(5, 305, 5):
            f.write(C18_cure_pp_template.format(c=c, j=j) + "\n\n")

# %%
