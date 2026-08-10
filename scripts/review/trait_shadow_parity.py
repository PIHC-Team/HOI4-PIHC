"""Review native PIHC3 trait artifacts against the PIHC_dev copy overlay."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from paradev.sdk import Project

PROJECT_ROOT = Path(__file__).resolve().parents[2]

ARTIFACT_PATTERNS = (
    "common/country_leader/{trait_id}.txt",
    "localisation/english/{trait_id}_l_english.yml",
    "localisation/simp_chinese/{trait_id}_l_simp_chinese.yml",
)


def main() -> None:
    """Run the trait shadow parity review and print JSON."""

    parser = argparse.ArgumentParser(description="Compare native PIHC3 trait artifacts against copied PIHC_dev files.")
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT, help="PIHC3 project root.")
    parser.add_argument(
        "--module-root",
        type=Path,
        default=None,
        help="Root containing src/modules/trait directories.",
    )
    parser.add_argument(
        "--native-root",
        type=Path,
        default=None,
        help="Generated native output root, usually build/mod.",
    )
    parser.add_argument(
        "--baseline-root",
        type=Path,
        required=True,
        help="Historical PIHC_dev baseline root.",
    )
    parser.add_argument(
        "--only",
        action="append",
        default=[],
        help="Review one trait tag or id; may be repeated.",
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Omit per-artifact rows from the JSON output.",
    )
    parser.add_argument(
        "--fail-on-diff",
        action="store_true",
        help="Exit with status 1 unless every artifact is exact.",
    )
    args = parser.parse_args()

    project = Project.load(args.project_root)
    module_root = args.module_root or project.root / "src" / "modules" / "trait"
    native_root = args.native_root or project.output_root
    only = [_normalize_trait_id(item) for item in args.only]
    try:
        summary = review_trait_shadow_parity(
            module_root=module_root,
            native_root=native_root,
            copy_root=args.baseline_root,
            only=only,
        )
    except ValueError as error:
        parser.error(str(error))
    if args.summary_only:
        summary = {key: value for key, value in summary.items() if key != "artifacts"}
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    if args.fail_on_diff and summary["status_counts"].get("exact", 0) != summary["artifact_count"]:
        raise SystemExit(1)


def review_trait_shadow_parity(
    *,
    module_root: Path,
    native_root: Path,
    copy_root: Path,
    only: list[str] | None = None,
) -> dict[str, Any]:
    """Compare native trait artifacts with copy-root artifacts.

    Args:
        module_root: Root containing `TRAIT_*` module directories.
        native_root: Built native output root.
        copy_root: PIHC_dev copy baseline root.
        only: Optional normalized `TRAIT_*` ids to review.

    Returns:
        JSON-serializable parity summary.
    """

    trait_ids = _trait_ids(module_root)
    if only:
        allowed = set(only)
        missing = sorted(allowed - set(trait_ids))
        if missing:
            raise ValueError(f"Unknown requested trait IDs: {', '.join(missing)}.")
        trait_ids = [trait_id for trait_id in trait_ids if trait_id in allowed]
    artifacts = [
        _compare_artifact(
            trait_id=trait_id,
            artifact_path=artifact_path,
            native_root=native_root,
            copy_root=copy_root,
        )
        for trait_id in trait_ids
        for artifact_path in _artifact_paths(trait_id)
    ]
    status_counts = Counter(row["status"] for row in artifacts)
    return {
        "schema": "pihc3.trait_shadow_parity.v1",
        "trait_count": len(trait_ids),
        "artifact_count": len(artifacts),
        "status_counts": dict(sorted(status_counts.items())),
        "artifacts": artifacts,
    }


def _trait_ids(module_root: Path) -> list[str]:
    if not module_root.is_dir():
        return []
    return [path.name for path in sorted(module_root.iterdir(), key=lambda item: item.name) if path.is_dir() and path.name.startswith("TRAIT_")]


def _artifact_paths(trait_id: str) -> list[str]:
    return [pattern.format(trait_id=trait_id) for pattern in ARTIFACT_PATTERNS]


def _compare_artifact(*, trait_id: str, artifact_path: str, native_root: Path, copy_root: Path) -> dict[str, Any]:
    native_path = native_root / artifact_path
    copy_path = copy_root / artifact_path
    native_exists = native_path.is_file()
    copy_exists = copy_path.is_file()
    status = _artifact_status(
        native_path=native_path,
        copy_path=copy_path,
        native_exists=native_exists,
        copy_exists=copy_exists,
    )
    return {
        "trait_id": trait_id,
        "artifact_path": artifact_path,
        "status": status,
        "native_sha256": _sha256(native_path) if native_exists else None,
        "copy_sha256": _sha256(copy_path) if copy_exists else None,
        "native_bytes": native_path.stat().st_size if native_exists else None,
        "copy_bytes": copy_path.stat().st_size if copy_exists else None,
    }


def _artifact_status(*, native_path: Path, copy_path: Path, native_exists: bool, copy_exists: bool) -> str:
    if not native_exists and not copy_exists:
        return "missing_both"
    if not native_exists:
        return "missing_native"
    if not copy_exists:
        return "missing_copy"
    if native_path.read_bytes() == copy_path.read_bytes():
        return "exact"
    return "different"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _normalize_trait_id(value: str) -> str:
    normalized = value.strip().upper()
    if normalized.startswith("TRAIT_"):
        return normalized
    return f"TRAIT_{normalized}"


if __name__ == "__main__":
    main()
