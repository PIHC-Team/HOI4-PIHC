"""Audit or safely compact PIHC3 state-lore sources and folder titles."""

from __future__ import annotations

import argparse
import base64
from collections.abc import Sequence
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
from paradev.pdx import PDXBlock, PDXEntry, PDXScalar
from paradev.portable_paths import portable_authoring_title
from paradev.sdk import Project

DEFAULT_PROJECT_ROOT = get_file_dir(get_file_dir(__file__, abs=True), abs=True)
STATE_LORE_COUNT = 79


@dataclass(frozen=True, slots=True)
class _Compaction:
    module_root: str
    object_id: str
    state_title: str
    variant_text: str | None
    retire_generated: bool
    rename: bool


def main() -> int:
    """Run the State Lore compaction audit or guarded migration.

    Args:
        None.

    Returns:
        int: Process exit code; zero means the audit or write completed.
    """

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-root",
        default=DEFAULT_PROJECT_ROOT,
        help="PIHC3 project root; defaults to the project containing this script.",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Apply the fully preflighted, resumable compaction.",
    )
    args = parser.parse_args()
    project_root = pj(str(args.project_root), abs=True)
    try:
        changes, compact_count, variant_count = _compaction_plan(project_root)
        result = {
            "schema": "pihc3.state-lore-compaction.v1",
            "blocked": False,
            "write": bool(args.write),
            "module_count": len(changes) + compact_count,
            "change_count": len(changes),
            "already_compact_count": compact_count,
            "conditional_variant_count": variant_count,
            "retired_generated_source_count": sum(2 for change in changes if change.retire_generated),
            "renamed_folder_count": sum(change.rename for change in changes),
            "change_module_ids": [change.object_id for change in changes],
        }
        if args.write and changes:
            _apply_compactions(project_root, changes)
            remaining, final_count, final_variant_count = _compaction_plan(project_root)
            if remaining or final_count != result["module_count"] or final_variant_count != variant_count:
                raise RuntimeError("State Lore compaction verification did not reach the complete compact state.")
            result["written"] = True
        else:
            result["written"] = False
        print(dumps_json(result))
        return 0
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        print(
            dumps_json(
                {
                    "schema": "pihc3.state-lore-compaction.v1",
                    "blocked": True,
                    "write": bool(args.write),
                    "error": str(error),
                }
            )
        )
        return 1


def _compaction_plan(
    project_root: str,
) -> tuple[tuple[_Compaction, ...], int, int]:
    modules_root = pj(project_root, "src/modules/state_lore")
    state_titles = _state_titles(project_root)
    module_roots = tuple(sorted(list_dirs(modules_root, abs=True)))
    if len(module_roots) != STATE_LORE_COUNT:
        raise ValueError(f"Expected {STATE_LORE_COUNT} state-lore modules, found {len(module_roots)}.")

    changes: list[_Compaction] = []
    compact_count = 0
    variant_count = 0
    targets: set[str] = set()
    for module_root in module_roots:
        module_name = get_file_basename(module_root)
        object_id, separator, current_title = module_name.partition(" - ")
        state_id = _state_id(object_id, label=module_name)
        if separator != " - " or not current_title:
            raise ValueError(f"State Lore folder {module_name!r} must use '<object id> - <title>'.")
        state_title = state_titles.get(str(state_id))
        if state_title is None:
            raise ValueError(f"State Lore {object_id!r} has no matching State module {state_id!r}.")
        expected_title = portable_authoring_title(state_title, object_id=object_id)
        if expected_title != state_title:
            raise ValueError(f"State module {state_id!r} has non-portable title {state_title!r}.")
        target_root = pj(modules_root, f"{object_id} - {state_title}")
        if target_root in targets:
            raise ValueError(f"State Lore target folder is duplicated: {target_root}.")
        targets.add(target_root)
        if target_root != module_root and exists_path(target_root):
            raise ValueError(f"State Lore target folder already exists: {target_root}.")

        localization_path = pj(module_root, "main.loc")
        if not exists_file(localization_path):
            raise ValueError(f"State Lore {object_id!r} is missing main.loc.")
        localization = parse_source(load_txt(localization_path, encoding="utf-8-sig", strict=True))
        if localization.issues:
            raise ValueError(f"State Lore {object_id!r} localization contains parse issues.")

        scripted_path = pj(module_root, "scripted_localisation.pdx")
        on_actions_path = pj(module_root, "on_actions.pdx")
        variants_path = pj(module_root, "variants.pdx")
        has_scripted = exists_file(scripted_path)
        has_on_actions = exists_file(on_actions_path)
        if has_scripted != has_on_actions:
            raise ValueError(f"State Lore {object_id!r} has only one generated aggregate fragment.")
        rename = current_title != state_title
        if has_scripted:
            if exists_path(variants_path):
                raise ValueError(f"State Lore {object_id!r} mixes generated fragments with variants.pdx.")
            variants = _legacy_variants(
                scripted_path,
                on_actions_path,
                object_id=object_id,
                state_id=state_id,
            )
            _validate_localization(
                localization.entries,
                object_id=object_id,
                variant_keys=tuple(key for key, _trigger in variants),
            )
            variant_text = _variant_text(variants) if variants else None
            if variant_text is not None:
                _validate_variant_text(
                    variant_text,
                    object_id=object_id,
                    label=variants_path,
                )
            variant_count += len(variants)
            changes.append(
                _Compaction(
                    module_root=module_root,
                    object_id=object_id,
                    state_title=state_title,
                    variant_text=variant_text,
                    retire_generated=True,
                    rename=rename,
                )
            )
            continue

        variant_keys: tuple[str, ...] = ()
        if exists_file(variants_path):
            variant_text = load_txt(variants_path, encoding="utf-8", strict=True)
            variant_keys = _validate_variant_text(
                variant_text,
                object_id=object_id,
                label=variants_path,
            )
        _validate_localization(
            localization.entries,
            object_id=object_id,
            variant_keys=variant_keys,
        )
        variant_count += len(variant_keys)
        if rename:
            changes.append(
                _Compaction(
                    module_root=module_root,
                    object_id=object_id,
                    state_title=state_title,
                    variant_text=None,
                    retire_generated=False,
                    rename=True,
                )
            )
        else:
            compact_count += 1
    return tuple(changes), compact_count, variant_count


def _state_titles(project_root: str) -> dict[str, str]:
    state_root = pj(project_root, "src/modules/state")
    titles: dict[str, str] = {}
    for module_root in sorted(list_dirs(state_root, abs=True)):
        module_name = get_file_basename(module_root)
        object_id, separator, title = module_name.partition(" - ")
        if separator != " - " or not object_id or not title:
            raise ValueError(f"State folder {module_name!r} must use '<state id> - <title>'.")
        if object_id in titles:
            raise ValueError(f"State id {object_id!r} has more than one module folder.")
        titles[object_id] = title
    return titles


def _legacy_variants(
    scripted_path: str,
    on_actions_path: str,
    *,
    object_id: str,
    state_id: int,
) -> tuple[tuple[str, PDXBlock], ...]:
    scripted = PDXBlock.from_file(scripted_path)
    name = _defined_text(scripted, "GetCurentStateLoreName", label=scripted_path)
    description = _defined_text(
        scripted,
        "GetCurentStateLoreDesc",
        label=scripted_path,
    )
    if len(scripted.entries) != 2:
        raise ValueError(f"{scripted_path} must contain exactly the name and description selectors.")
    expected_name = _defined_text_entry(
        "GetCurentStateLoreName",
        (
            _text_entry(
                _state_trigger(state_id),
                f"[{state_id}.GetName]",
            ),
        ),
    )
    if name.to_str() != _parsed_entry(expected_name).to_str():
        raise ValueError(f"{scripted_path} contains non-generated state-name selector edits.")

    text_blocks = [entry.val for entry in description.val.entries if entry.key_str == "text" and isinstance(entry.val, PDXBlock)]
    if len(description.val.entries) != len(text_blocks) + 1 or not text_blocks:
        raise ValueError(f"{scripted_path} description selector has unsupported fields.")
    variants: list[tuple[str, PDXBlock]] = []
    for index, text_block in enumerate(text_blocks):
        localization_key = _only_scalar(
            text_block,
            "localization_key",
            label=f"{scripted_path} description text {index + 1}",
        )
        trigger = _only_block(
            text_block,
            "trigger",
            label=f"{scripted_path} description text {index + 1}",
        )
        if len(text_block.entries) != 2:
            raise ValueError(f"{scripted_path} description text {index + 1} has unsupported fields.")
        extra = _trigger_extra(
            trigger,
            state_id=state_id,
            label=f"{scripted_path} description text {index + 1}",
        )
        is_last = index == len(text_blocks) - 1
        if is_last:
            if localization_key != object_id or extra.entries:
                raise ValueError(f"{scripted_path} must end with the generated default {object_id!r}.")
            continue
        if localization_key == object_id or not extra.entries:
            raise ValueError(f"{scripted_path} conditional description {index + 1} is not a real variant.")
        variants.append((localization_key, extra))

    expected_description = _defined_text_entry(
        "GetCurentStateLoreDesc",
        (
            *(
                _text_entry(
                    _state_trigger(state_id, extra_entries=trigger.entries),
                    localization_key,
                )
                for localization_key, trigger in variants
            ),
            _text_entry(_state_trigger(state_id), object_id),
        ),
    )
    if description.to_str() != _parsed_entry(expected_description).to_str():
        raise ValueError(f"{scripted_path} contains non-generated description selector edits.")

    on_actions = PDXBlock.from_file(on_actions_path)
    expected_on_actions = _on_actions_block(state_id)
    if on_actions.to_str() != _parsed_block(expected_on_actions).to_str():
        raise ValueError(f"{on_actions_path} contains non-generated startup registration edits.")
    return tuple(variants)


def _defined_text(block: PDXBlock, name: str, *, label: str) -> PDXEntry:
    matches = [
        entry for entry in block.entries if entry.key_str == "defined_text" and isinstance(entry.val, PDXBlock) and _optional_scalar(entry.val, "name") == name
    ]
    if len(matches) != 1:
        raise ValueError(f"{label} must contain exactly one defined_text {name!r}.")
    return matches[0]


def _trigger_extra(block: PDXBlock, *, state_id: int, label: str) -> PDXBlock:
    if not block.entries:
        raise ValueError(f"{label} has an empty trigger.")
    expected_check = _parsed_entry(_state_check_entry(state_id))
    if block.entries[0].to_str() != expected_check.to_str():
        raise ValueError(f"{label} does not start with generated state routing.")
    return PDXBlock.from_entries(entry.clone() for entry in block.entries[1:])


def _validate_variant_text(
    text: str,
    *,
    object_id: str,
    label: str,
) -> tuple[str, ...]:
    block = PDXBlock.from_str(text)
    keys: list[str] = []
    seen: set[str] = set()
    if not block.entries:
        raise ValueError(f"{label} is empty; remove the optional file instead.")
    for index, entry in enumerate(block.entries, start=1):
        if entry.key_str != "variant" or not isinstance(entry.val, PDXBlock):
            raise ValueError(f"{label} entry {index} must be a variant block.")
        if len(entry.val.entries) != 2:
            raise ValueError(f"{label} variant {index} must contain two fields.")
        key = _only_scalar(
            entry.val,
            "localization_key",
            label=f"{label} variant {index}",
        )
        trigger = _only_block(
            entry.val,
            "trigger",
            label=f"{label} variant {index}",
        )
        if not key.startswith(f"{object_id}_") or key in seen:
            raise ValueError(f"{label} variant {index} has invalid or repeated localization key {key!r}.")
        if not trigger.entries or _block_contains_key(trigger, "check_variable"):
            raise ValueError(f"{label} variant {index} must have a non-empty trigger without check_variable.")
        seen.add(key)
        keys.append(key)
    return tuple(keys)


def _validate_localization(
    entries: Sequence[SourceEntry],
    *,
    object_id: str,
    variant_keys: tuple[str, ...],
) -> None:
    localized = {(entry.language, entry.key) for entry in entries}
    languages = sorted(language for language, key in localized if key == object_id)
    if not languages:
        raise ValueError(f"State Lore {object_id!r} localization has no default lore text.")
    missing = [f"{language}.{key}" for key in variant_keys for language in languages if (language, key) not in localized]
    if missing:
        raise ValueError(f"State Lore {object_id!r} localization is missing: {', '.join(missing)}.")


def _variant_text(variants: tuple[tuple[str, PDXBlock], ...]) -> str:
    block = PDXBlock.from_entries(
        PDXEntry.kv(
            "variant",
            PDXBlock.from_entries(
                [
                    PDXEntry.kv_id("localization_key", localization_key),
                    PDXEntry.kv("trigger", trigger.clone()),
                ]
            ),
        )
        for localization_key, trigger in variants
    )
    return f"{block.to_str()}\n"


def _state_id(object_id: str, *, label: str) -> int:
    prefix = "STATE_LORE_"
    suffix = object_id[len(prefix) :] if object_id.startswith(prefix) else ""
    if not suffix.isdigit() or int(suffix) <= 0:
        raise ValueError(f"State Lore {label!r} must use STATE_LORE_<positive state id>.")
    return int(suffix)


def _optional_scalar(block: PDXBlock, key: str) -> str | None:
    values = [str(entry.val.val) for entry in block.entries if entry.key_str == key and isinstance(entry.val, PDXScalar)]
    return values[0] if len(values) == 1 else None


def _only_scalar(block: PDXBlock, key: str, *, label: str) -> str:
    value = _optional_scalar(block, key)
    if value is None or not value.strip():
        raise ValueError(f"{label} must contain exactly one non-empty {key} scalar.")
    return value.strip()


def _only_block(block: PDXBlock, key: str, *, label: str) -> PDXBlock:
    values = [entry.val for entry in block.entries if entry.key_str == key and isinstance(entry.val, PDXBlock)]
    if len(values) != 1:
        raise ValueError(f"{label} must contain exactly one {key} block.")
    return values[0]


def _block_contains_key(block: PDXBlock, key: str) -> bool:
    return any(entry.key_str == key or (isinstance(entry.val, PDXBlock) and _block_contains_key(entry.val, key)) for entry in block.entries)


def _state_check_entry(state_id: int) -> PDXEntry:
    return PDXEntry.kv(
        "check_variable",
        PDXBlock.from_entries([PDXEntry.kv_id("state_lore_text_state_id", f"{state_id}.id")]),
    )


def _parsed_entry(entry: PDXEntry) -> PDXEntry:
    return PDXBlock.from_str(entry.to_str()).entries[0]


def _parsed_block(block: PDXBlock) -> PDXBlock:
    return PDXBlock.from_str(block.to_str())


def _state_trigger(
    state_id: int,
    *,
    extra_entries: tuple[PDXEntry, ...] = (),
) -> PDXBlock:
    return PDXBlock.from_entries([_state_check_entry(state_id), *(entry.clone() for entry in extra_entries)])


def _text_entry(trigger: PDXBlock, localization_key: str) -> PDXEntry:
    return PDXEntry.kv(
        "text",
        PDXBlock.from_entries(
            [
                PDXEntry.kv("trigger", trigger),
                PDXEntry.kv_id("localization_key", localization_key),
            ]
        ),
    )


def _defined_text_entry(name: str, texts: tuple[PDXEntry, ...]) -> PDXEntry:
    return PDXEntry.kv(
        "defined_text",
        PDXBlock.from_entries([PDXEntry.kv_id("name", name), *(entry.clone() for entry in texts)]),
    )


def _on_actions_block(state_id: int) -> PDXBlock:
    return PDXBlock.from_entries(
        [
            PDXEntry.kv(
                "on_actions",
                PDXBlock.from_entries(
                    [
                        PDXEntry.kv(
                            "on_startup",
                            PDXBlock.from_entries(
                                [
                                    PDXEntry.kv(
                                        "effect",
                                        PDXBlock.from_entries(
                                            [
                                                PDXEntry.kv(
                                                    "add_to_array",
                                                    PDXBlock.from_entries(
                                                        [
                                                            PDXEntry.kv_id(
                                                                "global.states_with_lore",
                                                                f"{state_id}.id",
                                                            )
                                                        ]
                                                    ),
                                                )
                                            ]
                                        ),
                                    )
                                ]
                            ),
                        )
                    ]
                ),
            )
        ]
    )


def _apply_compactions(
    project_root: str,
    changes: tuple[_Compaction, ...],
) -> None:
    project = Project.load(project_root)
    for change in changes:
        removals = []
        if change.retire_generated:
            for name in ("scripted_localisation.pdx", "on_actions.pdx"):
                path = pj(change.module_root, name)
                source_stat = stat_path(path)
                removals.append(
                    {
                        "path": path,
                        "expected_size": source_stat.st_size,
                        "expected_mtime_ns": source_stat.st_mtime_ns,
                    }
                )
        replacements = []
        if change.variant_text is not None:
            replacements.append(
                {
                    "path": pj(change.module_root, "variants.pdx"),
                    "content_base64": base64.b64encode(change.variant_text.encode("utf-8")).decode("ascii"),
                    "expected_absent": True,
                }
            )
        rename = (
            {
                "module_id": f"state_lore/{change.object_id}",
                "object_id": change.object_id,
                "title": change.state_title,
            }
            if change.rename
            else None
        )
        project.apply_source_draft(
            source_removals=removals,
            source_replacements=replacements,
            module_rename=rename,
        )


if __name__ == "__main__":
    raise SystemExit(main())
