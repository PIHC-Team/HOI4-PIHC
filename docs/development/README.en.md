# Developing PIHC3 with ParaDev

[简体中文](README.zh.md) · [Repository home](../../README.md) · [Mod overview](../steam/STEAM_PROFILE.en.md)

This guide is for writers, translators, artists, testers, designers, and HoI4
modders. You do **not** need to be fluent in Python. ParaDev's desktop GUI owns
the normal create, edit, validate, and build workflow; text files and the Python
SDK are available when you want more control.

## 1. The ten-minute start

### What you need

- Python 3.10–3.13.
- Git for the current source install and clone, or a ParaDev wheel plus a repository ZIP supplied by a maintainer.
- A GitHub account to submit changes; `PIHC-Team/HOI4-PIHC` is public to read.
- Hearts of Iron IV only when you want to test the generated mod in game.

Python is the only runtime requirement. You do not need Conda, Node.js, Rust,
or an IDE. We recommend uv for the shortest isolated setup; Miniforge is an
optional Conda-compatible alternative when you prefer named environments.

### Install ParaDev with uv (recommended)

ParaDev's first PyPI release is being prepared. Install the current public
package source until that release is available. uv keeps ParaDev and its
dependencies in a dedicated environment and can obtain Python 3.12 for you:

```bash
uv tool install --python 3.12 \
  "paradev @ git+https://github.com/PIHC-Team/ParaDev.git"
```

If `paradev` is not found after installation, run `uv tool update-shell`, then
restart the terminal. Upgrade the source installation with `uv tool upgrade
paradev`. Once ParaDev is on PyPI, new installs simplify to `uv tool install
--python 3.12 paradev`.

Install uv from its [official instructions](https://docs.astral.sh/uv/getting-started/installation/).
The standalone uv installer does not require an existing Python installation.

### Optional: use a Miniforge environment

[Miniforge](https://github.com/conda-forge/miniforge) provides small,
Conda-compatible environments backed by conda-forge. After installing
Miniforge, create a project environment and install ParaDev inside it:

```bash
conda create --name pihc3 python=3.12 -y
conda activate pihc3
python -m pip install \
  "paradev @ git+https://github.com/PIHC-Team/ParaDev.git"
```

Activate `pihc3` before launching ParaDev. This workflow is supported, but it
is a convenience rather than a project requirement. Do not install packages
into Miniforge's `base` environment.

### Optional: use an existing Python virtual environment

If you already manage Python yourself, a standard virtual environment works:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install \
  "paradev @ git+https://github.com/PIHC-Team/ParaDev.git"
```

On Windows PowerShell, activate it with `.venv\Scripts\Activate.ps1`. Keep this
environment available whenever you launch ParaDev; uv tool and Miniforge avoid
accidentally mixing ParaDev with unrelated Python packages.

### Get PIHC3 and open the GUI

```bash
git clone https://github.com/PIHC-Team/HOI4-PIHC.git
cd HOI4-PIHC
paradev dashboard
```

In ParaDev, choose **Open project** and select the `HOI4-PIHC` folder containing
`paradev.yaml`. On macOS you may also install a Finder/Dock application:

```bash
paradev dashboard --install-app --yes
open "$HOME/Applications/ParaDev.app"
```

If the system WebView cannot open, `paradev dashboard --browser` uses a normal
browser tab and `paradev dashboard --app` uses an installed Chromium browser.

### Prove the checkout works

Open **Build**, choose **Update existing output**, and press **Build**. A clean
checkout should finish with no blocking diagnostics. The first build establishes
a complete output baseline; later cached and partial updates are faster.

If you do not want to write game output yet, run a read-only plan:

```bash
paradev build . --summary --json
```

## 2. The project model

Every ordinary piece of content is a self-contained module:

```text
src/modules/<family>/<OBJECT_ID> - <readable title>/
├── def.txt                     # gameplay definition
├── main.loc                    # localized name and description
├── preview.png                 # optional ParaDev preview
└── ...                         # family-owned icons, pictures, and resources
```

The object ID is the stable game/compiler identity. The title after ` - ` helps
people browse the project and normally uses PIHC3's preferred language, Chinese.
Use ParaDev's **Name**, **Rename**, or **Duplicate** actions so references and the
folder name stay synchronized.

Collections own grouped content such as a Focus tree:

```text
src/collections/focus/<TREE_ID> - <readable title>/
```

The important top-level folders are:

| Path | Who edits it | Purpose |
| --- | --- | --- |
| `src/modules/` | Most contributors | Standalone Ideas, Events, Focuses, Characters, Technologies, and other content. |
| `src/collections/` | Content designers | Focus trees and other grouped content. |
| `extensions/` | Advanced ParaDev/Python developers | PIHC3-only Entity schemas, resource slots, compilers, and tree providers. |
| `scripts/` | Maintainers | Validation and project maintenance utilities. |
| `.paradev/`, `build/`, generated mod output | ParaDev | Caches, manifests, hidden routing, and generated files. Do not hand-edit or commit them. |

Never create `_component`, `_asset_component`, `legacy`, or `inactive_modules`
source folders. Keep definitions, localization, and images inside the semantic
module that owns them. To omit a module temporarily, use the GUI's **Inactive**
field; ParaDev stores only the minimal supported metadata.

## 3. Your first contribution

1. Start from a current `master` and create a focused branch.
2. Open PIHC3 in ParaDev and run one whole-project cached build.
3. Create or edit one logical piece of content.
4. Use a module- or family-partial update while iterating.
5. Run a final whole-project cached build; use a clean rebuild when changing
   extensions, moving many resources, or investigating stale output.
6. Review the GUI diagnostics and `git diff` before committing.
7. Submit a pull request describing the gameplay intent and how you tested it.

```bash
git switch -c content/c99-friendship-workshops
git status --short
git diff --check
```

Do not mix unrelated balance, localization, image, and architecture changes in
one contribution. Small, playable slices are easier to review and repair.

## 4. Tutorial: create an Idea without coding

This example adds a national Idea that increases civilian factory output by 2%.

1. Open **Country → Ideas** in the Project Browser.
2. Choose **Create module**.
3. Enter object ID `IDEA_C99_FRIENDSHIP_WORKSHOPS`.
4. Set **Name** to `友谊工坊`.
5. Add a short description explaining the gameplay effect.
6. Set **Civilian industry factor** to `0.02`. ParaDev uses decimal modifiers,
   so `0.02` means 2%, not 0.02%.
7. Leave **Category** as `country` and the other advanced fields at their
   defaults unless the design requires something else.
8. Review the generated-file plan, then choose **Create module**.
9. Open the new module and check **Definition** and **Localization**.
10. On **Build → Buildable items**, select the Idea and choose **Safe partial
    update**. Finish with a whole-project cached build before submitting.

ParaDev creates:

```text
src/modules/idea/IDEA_C99_FRIENDSHIP_WORKSHOPS - 友谊工坊/
├── def.txt
└── main.loc
```

For a custom icon, the easiest beginner workflow is to select a clean Idea that
already owns an icon, choose **Duplicate**, enter the new object ID, review the
copy plan, and replace its image in the new module's resource editor. This keeps
DDS/GFX filenames and source ownership together. Do not create a separate asset
module.

### Optional Python equivalent

```python
from paradev import Project

project = Project.load(".")
plan = project.create_module(
    "idea",
    "IDEA_C99_FRIENDSHIP_WORKSHOPS",
    values={
        "title": "友谊工坊",
        "description": "社区工坊让民用生产更有效率。",
        "cic": 0.02,
    },
)
if plan["blocked"]:
    raise RuntimeError(plan["diagnostics"])
```

PIHC3's preferred language is Chinese, so the `language` field can normally be
omitted. The SDK, GUI, CLI, REST, MCP, and AI authoring flows use the same
validated template and guarded write transaction.

## 5. Tutorial: create an Event

This example creates one country event in a new namespace.

1. Open **Events → Events** and choose **Create module**.
2. Enter namespace/object ID `C99_FRIENDSHIP_FAIR`.
3. Set **Name** to `第一届友谊工坊展览会`.
4. Write the event body in **Description**.
5. Set **Option title** to `让展览开始吧！`.
6. Review and create the module.
7. Open **Definition**. The template creates event
   `C99_FRIENDSHIP_FAIR.1`, marks it `is_triggered_only = yes`, and supplies one
   option. Add triggers, effects, or extra options only if the story needs them.
8. Run a Safe partial update for this Event, then test it from the HoI4 console:

```text
event C99_FRIENDSHIP_FAIR.1
```

The new folder is:

```text
src/modules/event/C99_FRIENDSHIP_FAIR - 第一届友谊工坊展览会/
├── def.txt
└── main.loc
```

Use a unique, readable namespace. Keep every event in this story sequence and
its localization and pictures in the same module. For a pictured event, duplicate
a similar clean Event module and replace its owned picture resources; the Event
family accepts files under `gfx/event_pictures/` and `interface/events/` inside
the module.

## 6. Tutorial: add a Focus in the tree editor

Do not create a separate “focus tree module.” The collection owns the tree; each
Focus remains an independently editable module.

1. Open **Politics → Focuses**, then choose **Open Focus tree**.
2. Select the correct tree from the scope selector above the canvas.
3. Select the intended parent Focus. ParaDev prefills the tree, position parent,
   prerequisite, and a position one row below the selection.
4. Choose **Add graph item**.
5. Enter a stable Focus ID such as `FOCUS_C99_FRIENDSHIP_WORKSHOPS`.
6. Enter the Name and Description. Review X/Y position, prerequisite, and icon
   sprite under advanced fields.
7. Review the exact plan and apply it.
8. Inspect the new node in the graph and run a module-partial update.

To start a completely new tree, create a **Focus tree** collection first, then
open it in the same diagram editor. Tree membership is system-owned hidden
metadata; use the collection picker or tree editor instead of editing it.

The Technology and Military Industrial Organization views follow the same
pattern. Technology and Doctrine nodes are standalone modules. In the MIO view,
**Add graph item** creates a child trait inside the selected organization.

## 7. Localization, definitions, and images

### Localization

`main.loc` uses ParaDev's readable block format. Multiple languages may live in
the same owned localization file:

```text
[zh.IDEA_C99_FRIENDSHIP_WORKSHOPS]
友谊工坊

[zh.IDEA_C99_FRIENDSHIP_WORKSHOPS_desc]
社区工坊让民用生产更有效率。

[en.IDEA_C99_FRIENDSHIP_WORKSHOPS]
Friendship Workshops

[en.IDEA_C99_FRIENDSHIP_WORKSHOPS_desc]
Community workshops make civilian production more efficient.
```

Keep keys stable and add the `_desc` key when the family expects a description.
Use the Localization editor where possible: it validates keys and prevents the
encoding/header mistakes common in raw HoI4 YAML.

### Definitions

`def.txt` contains Clausewitz/PDX gameplay script. ParaDev provides guided forms
for common fields and a source editor for advanced effects, triggers, AI weights,
and nested blocks. Copy a nearby working pattern from the **same family**, change
only the required IDs/effects, and build the module immediately.

### Images and icons

- `preview.png` is an optional authoring preview.
- Compiled DDS and GFX files stay inside the module's family-owned resource paths.
- Replace assets through the resource editor so ParaDev validates file type,
  target path, and concurrent changes.
- Duplicate a similar module when you need a known-good multi-file image layout.
- Never put an icon in a separate `_asset_component` folder or a shared dump.

The active family template and resource editor are the source of truth for
accepted slots. If a new file type is not offered, ask a ParaDev extension
developer to add the slot instead of hiding the file in unrelated content.

## 8. Which module type should I choose?

| Goal | Start with | Notes |
| --- | --- | --- |
| Add a national spirit or timed effect | Idea | Name, description, modifiers, and optional icon belong together. |
| Tell a story or present player choices | Event | One namespace module may own a related event sequence and its pictures. |
| Add a political/economic action | Decision | Choose or create its Decision-category collection. |
| Extend a national route | Focus | Add it through the Focus tree diagram. |
| Add research or a research graph node | Technology | Use the Technology tree for positions and prerequisites. |
| Add a leader, advisor, or operative | Character | Keep portrait and localization with the Character. |
| Change a nation or map area | Country, State, Strategic Region | Prefer guided forms; map edits need careful game testing. |
| Add units or military content | Division, Equipment, Doctrine, Building | Use an existing related module as the design reference. |
| Add an arms organization | Military Industrial Organization | Edit its trait graph in the MIO tree view. |
| Add a custom PIHC3 story system | Superevent, Inventory Item, State Lore | These are project-local extension families and compile like built-in types. |
| Add shared scripted behavior | Scripted Effect, Scripted Trigger, On Action | Advanced PDX work; document callers and test in game. |

The GUI lists every currently authoring-ready family, including empty families.
If uncertain, search existing modules by the gameplay concept before creating a
new type or shared file.

## 9. Build modes and when to use them

| GUI action | CLI equivalent | Use it when |
| --- | --- | --- |
| **Update existing output** | `paradev build . --emit-artifacts --emit-manifests --no-sync-launcher-descriptor` | Normal whole-project verification using validated caches. |
| **Clean output and rebuild** | Add `--full-rebuild` | First publication, extension/layout changes, or suspected stale generated output. |
| **Safe partial update** on a Family | Add `--family idea` | Iterating on several modules of one type. |
| **Safe partial update** on a Module | Add `--family idea --module IDEA_C99_FRIENDSHIP_WORKSHOPS` | Fast feedback for one module. |
| Read-only plan | Omit `--emit-artifacts --emit-manifests` | Validate and inspect without writing generated output. |

Useful commands:

```bash
# Cached whole-project publication.
paradev build . --emit-artifacts --emit-manifests \
  --no-sync-launcher-descriptor --summary --json

# Clean/full publication.
paradev build . --emit-artifacts --emit-manifests --full-rebuild \
  --no-sync-launcher-descriptor --summary --json

# One module.
paradev build . --family idea --module IDEA_C99_FRIENDSHIP_WORKSHOPS \
  --emit-artifacts --emit-manifests --no-sync-launcher-descriptor \
  --summary --json
```

Partial builds preserve a valid whole-project baseline; they do not replace the
final whole-project check. “Validating publication” at 75% is a real safety
phase for PIHC3's large output and does not mean the build is frozen.

## 10. Diagnostics and common mistakes

| Symptom | What to do |
| --- | --- |
| Project will not open | Select the repository root containing `paradev.yaml`, not `src/` or one module folder. |
| Duplicate object ID | Search the family first and choose a globally unique, stable ID. |
| Malformed `ID - title` folder | Rename through ParaDev; do not repair only the folder name in Finder/Explorer. |
| Missing localization | Add the required name/description keys in the module's `main.loc`. |
| Icon/picture missing in game | Confirm the DDS, GFX declaration, and referenced sprite all live in the same module. |
| Partial build looks correct but the full build fails | Fix the whole-project diagnostic; partial success covers only its target. |
| Hidden `.paradev` file appears changed | Do not edit it manually. Revert accidental user edits or ask a maintainer if ParaDev generated a real migration. |
| Build writes to the wrong place | Set the project output/mod root in ParaDev Config, then run a whole-project build. |

Do not silence or bypass a blocking diagnostic. It usually protects module
identity, data ownership, path portability, or generated-output safety.

## 11. AI-assisted content creation

ParaDev exposes the same authoring templates to its AI chat, MCP, REST, CLI, and
Python SDK. In the GUI, choose the **Create content plan** profile and ask for a
small, explicit batch, for example:

> Create five Ideas named A, B, C, D, and E with civilian industry factors of
> 2%, 5%, 8%, 12%, and 16%.

Review every proposed object ID, field, file, and diagnostic before applying.
The agent creates a plan first; applying requires the matching guarded plan and
will not overwrite an independently changed module. AI output still needs lore,
balance, localization, build, and in-game review by a human contributor.

## 12. Before opening a pull request

- [ ] The change has one clear gameplay or content purpose.
- [ ] Object IDs are unique and folder names follow `ID - readable title`.
- [ ] Definitions, localization, images, and metadata stay with their owner.
- [ ] No `_component`, `_asset_component`, `legacy`, or `inactive_modules` folder was added.
- [ ] No generated `.paradev`, build, or mod-output files are included.
- [ ] The target module/family partial build passed.
- [ ] A final whole-project cached build passed with no blocking diagnostics.
- [ ] New gameplay was tested in HoI4 when applicable.
- [ ] Chinese and English text were reviewed, or missing translation is clearly reported.
- [ ] `git diff --check` passes and the pull request explains testing.

## 13. Further reading and help

- [ParaDev README](https://github.com/PIHC-Team/ParaDev)
- [ParaDev getting started](https://github.com/PIHC-Team/ParaDev/blob/master/docs/user-manual/getting-started.md)
- [Modules and collections](https://github.com/PIHC-Team/ParaDev/blob/master/docs/user-manual/modules-and-collections.md)
- [Builds and diagnostics](https://github.com/PIHC-Team/ParaDev/blob/master/docs/user-manual/build-and-diagnostics.md)
- [Python SDK guide](https://github.com/PIHC-Team/ParaDev/blob/master/docs/user-manual/sdk-python.md)
- [PIHC3 migration-complete note](../migration/README.md)

When asking for help, include the module family and object ID, what you expected,
the exact diagnostic, and whether the failure occurs in a partial, cached, or
clean build. Screenshots are useful, but copyable diagnostic text is better.
