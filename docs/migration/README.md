# PIHC3 migration status

PIHC3's source migration is complete. This directory intentionally contains
only this cutover note; Git history retains the former step-by-step importer
reports.

Current development uses:

- `src/modules/<family>/<id> - <preferred-language title>/` for independently
  editable modules;
- `src/collections/<family>/<id> - <preferred-language title>/` only when
  sibling context is a real compiler concept;
- `extensions/<family>/` for project-local HeavenBase compiler modules and,
  only for project-owned persistence types, Entity definitions;
- `templates/` plus ParaDev SDK, GUI, CLI, REST, and MCP authoring operations
  for creating or editing modules;
- `.paradev/` only for disposable caches or hidden system-managed metadata.

Definitions, localization, previews, icons, and compiled assets live with
their semantic owner. There are no live `_component`, `_asset_component`,
`legacy`, or `inactive_modules` source directories, and supported scripts do
not recreate them.
Duplicate `_legacy` backup assets are likewise removed when the canonical
asset exists. Active gameplay ids may still contain `LEGACY`; those are HoI4
content contracts, not migration sources.

Former family names are absent from the live source tree and project extension
descriptors. Run one clean build when moving from a pre-cutover checkout;
subsequent full, cached, family-partial, and module-partial builds use only the
current semantic family ids.

Use the project [README](../../README.md) for build commands and
the ParaDev [PIHC3 manual](https://github.com/PIHC-Team/ParaDev/blob/master/docs/user-manual/pihc3.md)
for current authoring workflows.
