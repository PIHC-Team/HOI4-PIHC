# The Pony in the High Castle — PIHC3

PIHC3 is the canonical, ParaDev-native source project for **The Pony in the
High Castle**, a Hearts of Iron IV total-conversion mod.

**Canonical unified release (2026-09-05):** [reconciliation and reproducible build](docs/releases/unified-20260905.md) · [standalone compiled download](https://github.com/Magolor/HOI4-PIHC-Compiled/releases/tag/unified-20260905).

**Languages:** [English](README.en.md) · [简体中文](README.zh.md)

## Start here

| I want to… | English | 简体中文 |
| --- | --- | --- |
| Learn about and play the mod | [Steam/player profile](docs/steam/STEAM_PROFILE.en.md) | [Steam/玩家介绍](docs/steam/STEAM_PROFILE.zh.md) |
| Help create content with the ParaDev GUI | [Developer guide](docs/development/README.en.md) | [开发指南](docs/development/README.zh.md) |
| Understand the completed PIHC2 → PIHC3 migration | [Migration note](docs/migration/README.md) | [迁移说明](docs/migration/README.md) |

## Develop PIHC3 without becoming a programmer first

ParaDev presents PIHC3 as understandable content modules: Ideas, Events,
Characters, Focuses, Technologies, Decisions, Countries, States, Equipment,
Doctrines, achievements, and PIHC3-specific systems such as Superevents,
Inventory Items, and State Lore. Most contributors can create or edit them in
the desktop GUI without writing Python.

ParaDev only requires Python. We recommend [uv](https://docs.astral.sh/uv/) to
manage a dedicated Python tool environment automatically. Miniforge is a good
optional alternative for contributors who prefer named Conda environments;
Conda itself is not a ParaDev requirement.

```bash
uv tool install --python 3.12 \
  "paradev @ git+https://github.com/PIHC-Team/ParaDev.git"
paradev dashboard
```

Open this repository's root folder—the directory containing `paradev.yaml`—in
ParaDev. The bilingual developer guide explains setup, safe editing, images and
localization, clean/cached/partial builds, testing, and pull requests. It also
contains step-by-step tutorials for creating an Idea, an Event, and a Focus.

## One simple project model

```text
src/modules/<family>/<OBJECT_ID> - <readable title>/
├── def.txt                     # gameplay definition
├── main.loc                    # localization
├── preview.png                 # optional editor preview
└── ...                         # family-owned images and other resources

src/collections/                # focus trees and other grouped content
extensions/                     # PIHC3 compiler/entity extensions
```

Ordinary content authors work in `src/modules/` and `src/collections/`. Do not
edit hidden `.paradev/` files, generated output, compiler extensions, or project
metadata unless the developer guide explicitly identifies that advanced task.

## Build safely

The GUI's **Build** page is the recommended interface. The installed CLI is
also available for verification and automation:

```bash
# Update the complete existing output using validated caches.
paradev build . --emit-artifacts --emit-manifests \
  --no-sync-launcher-descriptor --summary --json

# Remove ParaDev-owned generated output and rebuild everything.
paradev build . --emit-artifacts --emit-manifests --full-rebuild \
  --no-sync-launcher-descriptor --summary --json

# Rebuild one family or one module safely.
paradev build . --family idea --emit-artifacts --emit-manifests \
  --no-sync-launcher-descriptor --summary --json
paradev build . --family idea --module IDEA_C99_EXAMPLE \
  --emit-artifacts --emit-manifests --no-sync-launcher-descriptor \
  --summary --json
```

Read [the English developer guide](docs/development/README.en.md) or
[中文开发指南](docs/development/README.zh.md) before submitting content.

## Repository status and reuse

`master` is the canonical PIHC3 source. `legacy` preserves the consolidated
PIHC2 history. No repository-wide open-source license has been declared: do not
assume reuse or redistribution rights for code, writing, art, music, or other
assets. Contributors must have permission to submit every included asset.
