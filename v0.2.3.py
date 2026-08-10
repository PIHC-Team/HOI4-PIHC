# %%
import time
timer_start = time.time()
import os

# %%
from pyheaven import *
args = HeavenArguments.from_parser([
    SwitchArgumentDescriptor("force", short="f", help="Force not caching previous compilations."),
    SwitchArgumentDescriptor("publish", short="p", help="Push the compiled mod to the repository."),
    SwitchArgumentDescriptor("zip", short="z", help="Zip the compiled mod."),
    SwitchArgumentDescriptor("keep-data", short="k", help="Keep the data folder after compiling."),
])
if args.publish:
    args.zip = True
    args.keep_data = False
if args.zip:
    args.force = True

# %%
if not args.force:
    from scripts.copy_technology_scripted_effect import create_copy_technology_scripted_effect
    create_copy_technology_scripted_effect()
    from scripts.add_winter_penalties import add_winter_penalties
    add_winter_penalties()
    from scripts.update_scripted_locs import update_scripted_locs
    update_scripted_locs()
    from scripts.compile_jokes import compile_all_jokes
    compile_all_jokes()
    from scripts.add_random_pony_characters import add_random_pony_characters
    add_random_pony_characters()
    from scripts.compile_artifacts import compile_artifacts
    compile_artifacts()
    from scripts.rename_state_folders import rename_state_lores
    rename_state_lores()

# %%
from scripts.C00_create_a_new_mod import C00_create_a_new_mod
C00_create_a_new_mod()

# %%
from scripts.C01_build_the_map import C01_build_the_map
C01_build_the_map(force=args.force)

# %%
# This is removed from v0.2.2
# from scripts.C02_add_mirror_portal import C02_add_mirror_portal
# C02_add_mirror_portal(force=args.force)
# from scripts.C02_add_mirror_portal import C02_normal
# C02_normal(force=args.force)
# From v0.2.3, railways are added
from scripts.C02_add_mirror_portal import C02_add_continental_railways
C02_add_continental_railways(force=args.force)

# %%
from scripts.C03_add_gfxs import C03_add_gfxs
C03_add_gfxs()

# %%
from scripts.C04_add_countries import C04_add_countries
C04_add_countries(force=args.force)

# %%
from scripts.C05_add_characters import C05_add_characters
C05_add_characters(force=args.force)

# %%
from scripts.C06_add_ideas import C06_add_ideas
C06_add_ideas(force=args.force)

# %%
from scripts.C07_add_military import C07_add_military
C07_add_military(force=args.force)

# %%
from scripts.C08_add_decisions import C08_add_decisions
C08_add_decisions(force=args.force)

# %%
from scripts.C09_add_national_focuses import C09_add_national_focuses
C09_add_national_focuses(force=args.force)

# %%
from scripts.C10_add_events import C10_add_events
C10_add_events(force=args.force)

# %%
from scripts.C11_add_intel_agencies import C11_add_intel_agencies
C11_add_intel_agencies(force=args.force)

# %%
from scripts.C12_add_achievements import C12_add_achievements
C12_add_achievements(force=args.force)

# %%
from scripts.C13_add_inventory_items import C13_add_inventory_items
C13_add_inventory_items(force=args.force)

# %%
from scripts.C14_add_state_lores import C14_add_state_lores
C14_add_state_lores(force=args.force)

# %%
from scripts.C15_add_special_projects import C15_add_special_projects
C15_add_special_projects(force=args.force)

# %%
from scripts.C16_add_entities import C16_add_entities
C16_add_entities(force=args.force)

# %%
from hoi4dev import *
CompileMod()
if not args.keep_data:
    Delete(F("data"), rm=True)
    Delete(F("hoi4dev_settings"), rm=True)

# %%
from README_generator import *

# %%
CopyFile("README.en.md", "README.md", rm=True)
CopyFile("README.md", F("README.md"))
CopyFile("README.en.md", F("README.en.md"))
CopyFile("README.zh.md", F("README.zh.md"))
# CopyFile("README.steam.en.md", F("README.steam.en.md"))
# CopyFile("README.steam.zh.md", F("README.steam.zh.md"))

if ExistFile("README.en.pdf"):
    CopyFile("README.en.pdf", F("README.en.pdf"))
if ExistFile("README.zh.pdf"):
    CopyFile("README.zh.pdf", F("README.zh.pdf"))

# %%
CopyFile(".gitignore", F(".gitignore"))
CopyFile(".gitattributes", F(".gitattributes"))
CopyFile("version.bash", F("version.bash"))
CopyFile("./gitcmds/push_compiled.bash", F("push_compiled.bash"))
CopyFile("./gitcmds/clear_git.bash", F("clear_git.bash"))
if args.publish:
    CMD(f"cd \"{F('')}\" && bash push_compiled.bash")
CMD(f"cd \"{F('')}\" && bash clear_git.bash")
Delete(F("push_compiled.bash"), rm=True)
Delete(F("clear_git.bash"), rm=True)
Delete(F("version.bash"), rm=True)
Delete(F(".gitattributes"), rm=True)
Delete(F(".gitignore"), rm=True)
if args.zip:
    small_version = open("version.bash").read().split('=')[-1].strip().strip('"')
    desktop = expanduser("~/Desktop")
    mod_name = "PIHC_dev"
    print("Zipping:", f"cd \"{F('')}..\" && zip -q -r \"{pjoin(desktop, small_version+'.zip')}\" \"./{mod_name}\" \"./{mod_name}.mod\"")
    CMD(f"cd \"{F('')}..\" && zip -q -r \"{pjoin(desktop, small_version+'.zip')}\" \"./{mod_name}\" \"./{mod_name}.mod\"")

# %%
timer_end = time.time()
print(SUCCESS(f"Done. Compilation time: {int((timer_end-timer_start)//60)}m {(timer_end-timer_start)%60:.2f}s."))

# %%
