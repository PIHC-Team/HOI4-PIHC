"""Fail when PIHC3 authoring sources drift back to a retired layout."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import unicodedata
from dataclasses import asdict, dataclass
from pathlib import Path

from heavenbase.utils import load_yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_KINDS = ("modules", "collections")
IGNORED_HOUSEKEEPING_FILE_NAMES = frozenset({".DS_Store"})
FORBIDDEN_DIRECTORY_NAMES = frozenset({"inactive_collections", "inactive_modules", "legacy"})
FORBIDDEN_DIRECTORY_SUFFIXES = ("_asset_component", "_component")
FORBIDDEN_OBJECT_ID_PATTERN = re.compile(
    r"(?:^|_)(?:asset_component|component)(?:_|$)",
    flags=re.IGNORECASE,
)
FAMILY_PATTERN = re.compile(r"[a-z][a-z0-9_]*")
COPY_MARKER_PATTERN = re.compile(
    r"(?:^|[ ._-])(?:copy(?:[ _-]+\d+)?|副本|拷贝|复制品)(?:$|[ ._-])",
    flags=re.IGNORECASE,
)
VISIBLE_METADATA_KEYS = frozenset({"collection", "comment", "inactive"})


@dataclass(frozen=True)
class LayoutSummary:
    """Stable, serializable inventory for one successful source audit."""

    collection_families: int
    collections: int
    hidden_metadata_files: int
    module_families: int
    modules: int
    source_files: int
    visible_metadata_files: int


def audit_source_layout(project_root: Path) -> tuple[LayoutSummary, tuple[str, ...]]:
    """Return a compact inventory and every deterministic layout violation."""

    project_root = project_root.resolve()
    source_root = project_root / "src"
    errors: list[str] = []
    counts = {
        "collection_families": 0,
        "collections": 0,
        "hidden_metadata_files": 0,
        "module_families": 0,
        "modules": 0,
        "source_files": 0,
        "visible_metadata_files": 0,
    }

    if not source_root.is_dir():
        errors.append("missing source root: src")
        return LayoutSummary(**counts), tuple(errors)

    unexpected_source_entries = sorted(
        path.name for path in source_root.iterdir() if path.name not in SOURCE_KINDS and path.name not in IGNORED_HOUSEKEEPING_FILE_NAMES
    )
    if unexpected_source_entries:
        errors.append("src contains entries outside modules/ and collections/: " + ", ".join(unexpected_source_entries))

    for root, directory_names, _file_names in os.walk(project_root):
        directory_names[:] = sorted(name for name in directory_names if name != ".git")
        root_path = Path(root)
        for directory_name in directory_names:
            directory_path = root_path / directory_name
            relative = _relative(directory_path, project_root)
            folded_name = directory_name.casefold()
            if folded_name in FORBIDDEN_DIRECTORY_NAMES or folded_name.endswith(FORBIDDEN_DIRECTORY_SUFFIXES):
                errors.append(f"retired directory: {relative}")

    for path in sorted(source_root.rglob("*")):
        if path.name in IGNORED_HOUSEKEEPING_FILE_NAMES:
            continue
        if path.is_symlink():
            errors.append(f"source symlink is not self-contained: {_relative(path, project_root)}")
        if path.is_dir() and not any(path.iterdir()):
            errors.append(f"source directory is empty: {_relative(path, project_root)}")
        if COPY_MARKER_PATTERN.search(path.name):
            errors.append(f"source path contains a copy marker: {_relative(path, project_root)}")

    for source_kind in SOURCE_KINDS:
        kind_root = source_root / source_kind
        if not kind_root.is_dir():
            errors.append(f"missing source kind: src/{source_kind}")
            continue
        direct_files = sorted(path for path in kind_root.iterdir() if path.is_file() and path.name not in IGNORED_HOUSEKEEPING_FILE_NAMES)
        for path in direct_files:
            errors.append(f"file must be inside a source family: {_relative(path, project_root)}")

        family_paths = sorted(path for path in kind_root.iterdir() if path.is_dir())
        counts[f"{source_kind[:-1]}_families"] = len(family_paths)
        for family_path in family_paths:
            family = family_path.name
            if FAMILY_PATTERN.fullmatch(family) is None:
                errors.append(f"source family must use a lower-case registry id: " f"{_relative(family_path, project_root)}")
            direct_family_files = sorted(path for path in family_path.iterdir() if path.is_file() and path.name not in IGNORED_HOUSEKEEPING_FILE_NAMES)
            for path in direct_family_files:
                errors.append(f"file must be inside an id - title source unit: " f"{_relative(path, project_root)}")

            object_ids: dict[str, Path] = {}
            unit_paths = sorted(path for path in family_path.iterdir() if path.is_dir())
            counts[source_kind] += len(unit_paths)
            for unit_path in unit_paths:
                object_id, separator, title = unit_path.name.partition(" - ")
                relative = _relative(unit_path, project_root)
                if separator != " - " or not object_id.strip() or not title.strip():
                    errors.append(f"source unit must use id - title: {relative}")
                    continue
                if object_id != object_id.strip() or title != title.strip():
                    errors.append(f"source unit contains surrounding whitespace: {relative}")
                if unicodedata.normalize("NFC", unit_path.name) != unit_path.name:
                    errors.append(f"source unit name is not NFC-normalized: {relative}")
                if FORBIDDEN_OBJECT_ID_PATTERN.search(object_id):
                    errors.append(f"source unit uses a retired component id: {relative}")
                duplicate = object_ids.setdefault(object_id.casefold(), unit_path)
                if duplicate != unit_path:
                    errors.append(f"duplicate object id {object_id!r}: " f"{_relative(duplicate, project_root)}, {relative}")

                authored_files = tuple(
                    path
                    for path in unit_path.rglob("*")
                    if path.is_file() and path.name not in IGNORED_HOUSEKEEPING_FILE_NAMES and ".paradev" not in path.relative_to(unit_path).parts
                )
                if not authored_files:
                    errors.append(f"source unit has no authored files: {relative}")
                counts["source_files"] += len(authored_files)
                counts["hidden_metadata_files"] += sum(1 for path in unit_path.rglob(".paradev/*.yaml") if path.is_file())
                _check_visible_metadata(
                    unit_path,
                    project_root=project_root,
                    errors=errors,
                    counts=counts,
                )

    return LayoutSummary(**counts), tuple(sorted(set(errors)))


def _check_visible_metadata(
    unit_path: Path,
    *,
    project_root: Path,
    errors: list[str],
    counts: dict[str, int],
) -> None:
    yml_path = unit_path / "meta.yml"
    if yml_path.exists():
        errors.append(f"visible metadata must use meta.yaml: {_relative(yml_path, project_root)}")
    metadata_path = unit_path / "meta.yaml"
    if not metadata_path.exists():
        return
    counts["visible_metadata_files"] += 1
    if not metadata_path.is_file():
        errors.append(f"visible metadata is not a file: {_relative(metadata_path, project_root)}")
        return
    try:
        metadata = load_yaml(str(metadata_path), strict=True)
    except Exception as exc:  # noqa: BLE001 - report parser diagnostics as audit output.
        errors.append(f"visible metadata is invalid: {_relative(metadata_path, project_root)} " f"({exc})")
        return
    if not isinstance(metadata, dict):
        errors.append(f"visible metadata must be a mapping: {_relative(metadata_path, project_root)}")
        return
    unknown_keys = sorted(str(key) for key in set(metadata) - VISIBLE_METADATA_KEYS)
    if unknown_keys:
        errors.append(f"visible metadata has system-owned keys at " f"{_relative(metadata_path, project_root)}: {', '.join(unknown_keys)}")


def _relative(path: Path, project_root: Path) -> str:
    try:
        return path.relative_to(project_root).as_posix()
    except ValueError:
        return path.as_posix()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-root",
        type=Path,
        default=PROJECT_ROOT,
        help="PIHC3 project root.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the stable audit result as JSON.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Print nothing when the audit passes.",
    )
    args = parser.parse_args()

    summary, errors = audit_source_layout(args.project_root)
    payload = {
        "schema": "pihc3.source-layout-audit.v1",
        "ok": not errors,
        "summary": asdict(summary),
        "errors": list(errors),
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    elif errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
    elif not args.quiet:
        print(
            "PIHC3 source layout passed: "
            f"{summary.modules} modules, {summary.collections} collections, "
            f"{summary.visible_metadata_files} visible metadata files."
        )
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
