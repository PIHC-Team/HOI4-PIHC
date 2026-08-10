"""Audit or safely compact PIHC3 inventory-item generated helper sources."""

from __future__ import annotations

import argparse
import base64
import sys
from dataclasses import dataclass
from os import stat as stat_path

from heavenbase.utils import (
    dumps_json,
    exists_file,
    exists_path,
    get_file_basename,
    get_file_dir,
    list_dirs,
    load_txt,
    pj,
)
from paradev.localization._source import SourceEntry, parse_source
from paradev.pdx import PDXBlock
from paradev.sdk import Project

PROJECT_ROOT = get_file_dir(get_file_dir(__file__, abs=True), abs=True)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from extensions.inventory_item.definition import (
    INVENTORY_ITEM_DEFINITION_PATH,
    STANDARD_HELPER_QUANTITIES,
    STANDARD_HELPER_QUANTITIES_TEXT,
    generated_inventory_localization_values,
    inventory_effects_block,
    inventory_triggers_block,
    is_generated_inventory_localization_key,
    load_inventory_item_definition,
)

MODULES_ROOT = pj(PROJECT_ROOT, "src/modules/inventory_item")


@dataclass(frozen=True, slots=True)
class _Migration:
    module_root: str
    object_id: str
    definition_text: str
    localization_text: str


@dataclass(frozen=True, slots=True)
class _Retirement:
    module_root: str
    object_id: str


def main() -> int:
    """Run the inventory compaction audit or guarded two-phase migration."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write",
        action="store_true",
        help="Apply the preflighted, resumable source compaction.",
    )
    args = parser.parse_args()
    try:
        migrations, retirements, already_compact = _migration_plan()
        result = {
            "schema": "pihc3.inventory-item-compaction.v1",
            "blocked": False,
            "write": bool(args.write),
            "module_count": len(migrations) + len(retirements) + already_compact,
            "migration_count": len(migrations),
            "pending_retirement_count": len(retirements),
            "already_compact_count": already_compact,
            "created_definition_count": len(migrations),
            "compacted_localization_count": len(migrations),
            "retired_generated_source_count": (len(migrations) + len(retirements)) * 2,
        }
        if args.write and (migrations or retirements):
            _apply_migrations(migrations, retirements=retirements)
            remaining, pending_retirements, compact_count = _migration_plan()
            if (
                remaining
                or pending_retirements
                or compact_count != result["module_count"]
            ):
                raise RuntimeError(
                    "Inventory compaction verification did not reach the complete compact state."
                )
            result["written"] = True
        else:
            result["written"] = False
        print(dumps_json(result))
        return 0
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        print(
            dumps_json(
                {
                    "schema": "pihc3.inventory-item-compaction.v1",
                    "blocked": True,
                    "write": bool(args.write),
                    "error": str(error),
                }
            )
        )
        return 1


def _migration_plan() -> tuple[tuple[_Migration, ...], tuple[_Retirement, ...], int]:
    modules = tuple(sorted(list_dirs(MODULES_ROOT, abs=True)))
    if len(modules) != 80:
        raise ValueError(f"Expected 80 inventory-item modules, found {len(modules)}.")
    migrations: list[_Migration] = []
    retirements: list[_Retirement] = []
    compact_count = 0
    for module_root in modules:
        module_name = get_file_basename(module_root)
        object_id = module_name.split(" - ", 1)[0]
        definition_path = pj(module_root, INVENTORY_ITEM_DEFINITION_PATH)
        effects_path = pj(module_root, "effects.txt")
        triggers_path = pj(module_root, "triggers.txt")
        localization_path = pj(module_root, "main.loc")
        legacy_state = exists_file(effects_path) or exists_file(triggers_path)
        if exists_file(definition_path):
            _validate_compact_module(
                module_root,
                object_id=object_id,
                allow_retired_sources=legacy_state,
            )
            if legacy_state:
                if not exists_file(effects_path) or not exists_file(triggers_path):
                    raise ValueError(
                        f"Inventory item {module_name!r} has only one retired generated helper file."
                    )
                retirements.append(
                    _Retirement(module_root=module_root, object_id=object_id)
                )
            else:
                compact_count += 1
            continue
        if not exists_file(effects_path) or not exists_file(triggers_path):
            raise ValueError(
                f"Inventory item {module_name!r} must contain either item.json or both generated helper files."
            )
        if not exists_file(localization_path):
            raise ValueError(f"Inventory item {module_name!r} is missing main.loc.")
        _validate_generated_pdx(effects_path, triggers_path, object_id=object_id)
        localization_text = load_txt(
            str(localization_path),
            encoding="utf-8-sig",
            strict=True,
        )
        compact_localization = _compact_localization(
            localization_text,
            object_id=object_id,
            label=str(localization_path),
        )
        definition_text = dumps_json(
            {"helper_quantities": STANDARD_HELPER_QUANTITIES_TEXT},
            indent=2,
        )
        if not definition_text.endswith("\n"):
            definition_text += "\n"
        load_inventory_item_definition(
            definition_text,
            label=str(definition_path),
        )
        migrations.append(
            _Migration(
                module_root=module_root,
                object_id=object_id,
                definition_text=definition_text,
                localization_text=compact_localization,
            )
        )
    return tuple(migrations), tuple(retirements), compact_count


def _validate_generated_pdx(
    effects_path: str,
    triggers_path: str,
    *,
    object_id: str,
) -> None:
    effects = PDXBlock.from_file(effects_path).to_str()
    generated_effects = inventory_effects_block(
        object_id,
        STANDARD_HELPER_QUANTITIES,
    ).to_str()
    if effects != generated_effects:
        raise ValueError(
            f"Inventory item {object_id!r} effects.txt contains non-generated edits and cannot be retired."
        )
    triggers = PDXBlock.from_file(triggers_path).to_str()
    generated_triggers = inventory_triggers_block(
        object_id,
        STANDARD_HELPER_QUANTITIES,
    ).to_str()
    if triggers != generated_triggers:
        raise ValueError(
            f"Inventory item {object_id!r} triggers.txt contains non-generated edits and cannot be retired."
        )


def _compact_localization(text: str, *, object_id: str, label: str) -> str:
    document = parse_source(text)
    if document.issues:
        raise ValueError(f"Inventory item localization contains parse issues: {label}")
    generated_values = generated_inventory_localization_values(
        object_id,
        STANDARD_HELPER_QUANTITIES,
        tuple(
            _localization_entry(entry, module_id=f"inventory_item/{object_id}")
            for entry in document.entries
        ),
    )
    generated_entries: list[SourceEntry] = []
    for entry in document.entries:
        if not is_generated_inventory_localization_key(object_id, entry.key):
            continue
        expected = generated_values.get((entry.language, entry.key))
        if expected != entry.text:
            raise ValueError(
                f"Inventory item {object_id!r} localization key {entry.key!r} contains a custom value and cannot be generated safely."
            )
        generated_entries.append(entry)
    if len(generated_entries) != len(generated_values):
        missing = sorted(
            f"{language}.{key}"
            for language, key in generated_values
            if not any(
                entry.language == language and entry.key == key
                for entry in generated_entries
            )
        )
        raise ValueError(
            f"Inventory item {object_id!r} localization is missing generated keys: {', '.join(missing[:8])}."
        )
    compact = text
    for entry in sorted(
        generated_entries, key=lambda item: item.entry_start, reverse=True
    ):
        compact = compact[: entry.entry_start] + compact[entry.entry_end :]
    compact_document = parse_source(compact)
    if compact_document.issues:
        raise ValueError(
            f"Inventory item {object_id!r} compact localization would be malformed."
        )
    if any(
        is_generated_inventory_localization_key(object_id, entry.key)
        for entry in compact_document.entries
    ):
        raise ValueError(
            f"Inventory item {object_id!r} compact localization retained generated keys."
        )
    return compact


def _localization_entry(entry: SourceEntry, *, module_id: str):
    from paradev.build import LocalizationEntry

    return LocalizationEntry(
        key=entry.key,
        language=entry.language,
        text=entry.text,
        source_path="main.loc",
        module_id=module_id,
    )


def _validate_compact_module(
    module_root: str,
    *,
    object_id: str,
    allow_retired_sources: bool,
) -> None:
    definition_path = pj(module_root, INVENTORY_ITEM_DEFINITION_PATH)
    definition = load_inventory_item_definition(
        load_txt(str(definition_path), encoding="utf-8", strict=True),
        label=str(definition_path),
    )
    if definition.helper_quantities != STANDARD_HELPER_QUANTITIES:
        raise ValueError(
            f"Migrated inventory item {object_id!r} must retain the standard helper quantities."
        )
    localization = parse_source(
        load_txt(pj(module_root, "main.loc"), encoding="utf-8-sig", strict=True)
    )
    if localization.issues:
        raise ValueError(
            f"Migrated inventory item {object_id!r} localization contains parse issues."
        )
    if any(
        is_generated_inventory_localization_key(object_id, entry.key)
        for entry in localization.entries
    ):
        raise ValueError(
            f"Migrated inventory item {object_id!r} still authors compiler-generated localization."
        )
    if not allow_retired_sources and any(
        exists_path(pj(module_root, name)) for name in ("effects.txt", "triggers.txt")
    ):
        raise ValueError(
            f"Migrated inventory item {object_id!r} still contains retired generated helper files."
        )


def _apply_migrations(
    migrations: tuple[_Migration, ...],
    *,
    retirements: tuple[_Retirement, ...],
) -> None:
    project = Project.load(PROJECT_ROOT)
    if retirements:
        _retire_generated_sources(
            project,
            tuple(retirement.module_root for retirement in retirements),
        )
    for start in range(0, len(migrations), 64):
        batch = migrations[start : start + 64]
        _apply_migration_batch(project, batch)
        _retire_generated_sources(
            project,
            tuple(migration.module_root for migration in batch),
        )


def _apply_migration_batch(
    project: Project,
    migrations: tuple[_Migration, ...],
) -> None:
    source_edits = []
    source_replacements = []
    for migration in migrations:
        localization_path = pj(migration.module_root, "main.loc")
        localization_stat = stat_path(localization_path)
        source_edits.append(
            {
                "path": localization_path,
                "text": migration.localization_text,
                "expected_size": localization_stat.st_size,
                "expected_mtime_ns": localization_stat.st_mtime_ns,
            }
        )
        source_replacements.append(
            {
                "path": pj(
                    migration.module_root,
                    INVENTORY_ITEM_DEFINITION_PATH,
                ),
                "content_base64": base64.b64encode(
                    migration.definition_text.encode("utf-8")
                ).decode("ascii"),
                "expected_absent": True,
            }
        )
    project.apply_source_draft(
        source_edits=source_edits,
        source_replacements=source_replacements,
    )


def _retire_generated_sources(
    project: Project,
    module_roots: tuple[str, ...],
) -> None:
    source_removals = []
    for module_root in module_roots:
        for name in ("effects.txt", "triggers.txt"):
            path = pj(module_root, name)
            source_stat = stat_path(path)
            source_removals.append(
                {
                    "path": path,
                    "expected_size": source_stat.st_size,
                    "expected_mtime_ns": source_stat.st_mtime_ns,
                }
            )
    project.apply_source_draft(source_removals=source_removals)


if __name__ == "__main__":
    raise SystemExit(main())
