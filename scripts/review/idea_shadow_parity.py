"""Review native PIHC3 idea artifacts against the PIHC_dev copy overlay."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from paradev.pdx import PDXBlock
from paradev.sdk import Project

PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOC_ENTRY_START_RE = re.compile(r'^\s*(?P<key>[^:#\s][^:]*?)\s*:\s*(?:\d+\s*)?"(?P<text>.*)$')


def main() -> None:
    """Run the idea shadow parity review and print JSON."""

    parser = argparse.ArgumentParser(description="Compare native PIHC3 idea artifacts against copied PIHC_dev files.")
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT, help="PIHC3 project root.")
    parser.add_argument(
        "--source-map",
        type=Path,
        default=None,
        help="Build source-map path from `paradev build --emit-manifests`.",
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
        help="Review one idea tag or id; may be repeated.",
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Omit per-artifact rows from the JSON output.",
    )
    parser.add_argument(
        "--fail-on-diff",
        action="store_true",
        help="Exit with status 1 unless every artifact is byte-exact.",
    )
    parser.add_argument(
        "--fail-on-normalized-diff",
        action="store_true",
        help="Exit with status 1 unless every artifact is byte-exact or normalized-equivalent.",
    )
    args = parser.parse_args()

    project = Project.load(args.project_root)
    source_map_path = args.source_map or project.build_root / "source-map.json"
    native_root = args.native_root or project.output_root
    only = [_normalize_idea_id(item) for item in args.only]
    try:
        summary = review_idea_shadow_parity(
            source_map_path=source_map_path,
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
    if args.fail_on_normalized_diff:
        acceptable = summary["normalized_status_counts"].get("exact", 0) + summary["normalized_status_counts"].get("equivalent", 0)
        if acceptable != summary["artifact_count"]:
            raise SystemExit(1)


def review_idea_shadow_parity(
    *,
    source_map_path: Path,
    native_root: Path,
    copy_root: Path,
    only: list[str] | None = None,
) -> dict[str, Any]:
    """Compare native idea artifacts with copy-root artifacts.

    Args:
        source_map_path: Build source-map path emitted by `paradev build --emit-manifests`.
        native_root: Built native output root.
        copy_root: PIHC_dev copy baseline root.
        only: Optional normalized `IDEA_*` ids to review.

    Returns:
        JSON-serializable parity summary.
    """

    rows = _idea_source_rows(source_map_path)
    if only:
        allowed = set(only)
        available = {row["idea_id"] for row in rows}
        missing = sorted(allowed - available)
        if missing:
            raise ValueError(f"Unknown requested idea IDs: {', '.join(missing)}.")
        rows = [row for row in rows if row["idea_id"] in allowed]
    artifacts = [
        _compare_artifact(
            idea_id=row["idea_id"],
            artifact_path=row["artifact_path"],
            native_root=native_root,
            copy_root=copy_root,
        )
        for row in rows
    ]
    _apply_global_loc_parity(artifacts, native_root=native_root, copy_root=copy_root)
    status_counts = Counter(row["status"] for row in artifacts)
    bucket_status_counts = Counter(f"{_artifact_bucket(row['artifact_path'])}:{row['status']}" for row in artifacts)
    normalized_status_counts = Counter(row["normalized_status"] for row in artifacts)
    bucket_normalized_status_counts = Counter(f"{_artifact_bucket(row['artifact_path'])}:{row['normalized_status']}" for row in artifacts)
    parity_status_counts = Counter(row["parity_status"] for row in artifacts)
    bucket_parity_status_counts = Counter(f"{_artifact_bucket(row['artifact_path'])}:{row['parity_status']}" for row in artifacts)
    return {
        "schema": "pihc3.idea_shadow_parity.v1",
        "idea_count": len({row["idea_id"] for row in rows}),
        "artifact_count": len(artifacts),
        "status_counts": dict(sorted(status_counts.items())),
        "bucket_status_counts": dict(sorted(bucket_status_counts.items())),
        "normalized_status_counts": dict(sorted(normalized_status_counts.items())),
        "bucket_normalized_status_counts": dict(sorted(bucket_normalized_status_counts.items())),
        "parity_status_counts": dict(sorted(parity_status_counts.items())),
        "bucket_parity_status_counts": dict(sorted(bucket_parity_status_counts.items())),
        "artifacts": artifacts,
    }


def _idea_source_rows(source_map_path: Path) -> list[dict[str, str]]:
    payload = json.loads(source_map_path.read_text(encoding="utf-8"))
    rows: list[dict[str, str]] = []
    for row in payload.get("source_map", []):
        owner = row.get("owner")
        artifact_path = row.get("artifact_path")
        target_root = row.get("target_root")
        if not isinstance(owner, str) or not owner.startswith("module:idea/"):
            continue
        if not isinstance(artifact_path, str) or target_root != "output":
            continue
        rows.append(
            {
                "idea_id": owner.removeprefix("module:idea/"),
                "artifact_path": artifact_path,
            }
        )
    return sorted(rows, key=lambda item: (item["idea_id"], item["artifact_path"]))


def _compare_artifact(*, idea_id: str, artifact_path: str, native_root: Path, copy_root: Path) -> dict[str, Any]:
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
    normalized_status = _normalized_artifact_status(
        artifact_path=artifact_path,
        native_path=native_path,
        copy_path=copy_path,
        status=status,
    )
    parity_status = _parity_artifact_status(
        artifact_path=artifact_path,
        native_path=native_path,
        copy_path=copy_path,
        normalized_status=normalized_status,
    )
    return {
        "idea_id": idea_id,
        "artifact_path": artifact_path,
        "status": status,
        "normalized_status": normalized_status,
        "parity_status": parity_status,
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


def _normalized_artifact_status(*, artifact_path: str, native_path: Path, copy_path: Path, status: str) -> str:
    if status != "different":
        return status
    if _normalized_equal(artifact_path=artifact_path, native_path=native_path, copy_path=copy_path):
        return "equivalent"
    return "different"


def _parity_artifact_status(*, artifact_path: str, native_path: Path, copy_path: Path, normalized_status: str) -> str:
    if normalized_status != "different":
        return normalized_status
    if artifact_path.startswith("localisation/") and _has_only_extra_native_empty_desc(native_path=native_path, copy_path=copy_path):
        return "compatible_extra_empty_desc"
    return normalized_status


def _apply_global_loc_parity(artifacts: list[dict[str, Any]], *, native_root: Path, copy_root: Path) -> None:
    native_index = _native_loc_index(artifacts, native_root=native_root)
    for artifact in artifacts:
        if artifact["parity_status"] != "different" or not artifact["artifact_path"].startswith("localisation/"):
            continue
        if _has_only_compatible_global_loc_drift(
            artifact_path=str(artifact["artifact_path"]),
            native_path=native_root / str(artifact["artifact_path"]),
            copy_path=copy_root / str(artifact["artifact_path"]),
            native_index=native_index,
        ):
            artifact["parity_status"] = "compatible_shared_loc_elsewhere"


def _native_loc_index(artifacts: list[dict[str, Any]], *, native_root: Path) -> dict[tuple[str, str], set[str]]:
    index: dict[tuple[str, str], set[str]] = {}
    for artifact in artifacts:
        artifact_path = str(artifact["artifact_path"])
        if not artifact_path.startswith("localisation/"):
            continue
        native_path = native_root / artifact_path
        if not native_path.is_file():
            continue
        loc = _normalized_loc(native_path)
        language = str(loc["language"])
        for key, text in loc["entries"]:
            index.setdefault((language, key), set()).add(text)
    return index


def _has_only_compatible_global_loc_drift(
    *,
    artifact_path: str,
    native_path: Path,
    copy_path: Path,
    native_index: dict[tuple[str, str], set[str]],
) -> bool:
    if not artifact_path.startswith("localisation/"):
        return False
    native = _normalized_loc(native_path)
    copied = _normalized_loc(copy_path)
    if native["language"] != copied["language"]:
        return False
    native_entries = dict(native["entries"])
    copied_entries = dict(copied["entries"])
    extra_native = {key: text for key, text in native_entries.items() if key not in copied_entries}
    missing_native = {key: text for key, text in copied_entries.items() if key not in native_entries}
    changed = {key for key in native_entries.keys() & copied_entries.keys() if native_entries[key] != copied_entries[key]}
    if changed or any(not key.endswith("_desc") or text for key, text in extra_native.items()):
        return False
    language = str(native["language"])
    return bool(missing_native) and all(text in native_index.get((language, key), set()) for key, text in missing_native.items())


def _has_only_extra_native_empty_desc(*, native_path: Path, copy_path: Path) -> bool:
    native = _normalized_loc(native_path)
    copied = _normalized_loc(copy_path)
    if native["language"] != copied["language"]:
        return False
    native_entries = dict(native["entries"])
    copied_entries = dict(copied["entries"])
    extra_native = {key: text for key, text in native_entries.items() if key not in copied_entries}
    missing_native = {key for key in copied_entries if key not in native_entries}
    changed = {key for key in native_entries.keys() & copied_entries.keys() if native_entries[key] != copied_entries[key]}
    return bool(extra_native) and not missing_native and not changed and all(key.endswith("_desc") and text == "" for key, text in extra_native.items())


def _normalized_equal(*, artifact_path: str, native_path: Path, copy_path: Path) -> bool:
    if artifact_path.startswith("common/") and artifact_path.endswith(".txt"):
        return _normalized_pdx(native_path) == _normalized_pdx(copy_path)
    if artifact_path.startswith("localisation/") and artifact_path.endswith(".yml"):
        return _normalized_loc(native_path) == _normalized_loc(copy_path)
    return False


def _normalized_pdx(path: Path) -> Any:
    return PDXBlock.from_str(path.read_text(encoding="utf-8-sig", errors="replace")).to_dict()


def _normalized_loc(path: Path) -> dict[str, Any]:
    language = ""
    entries: list[tuple[str, str]] = []
    lines = path.read_text(encoding="utf-8-sig", errors="replace").splitlines()
    index = 0
    while index < len(lines):
        raw_line = lines[index]
        index += 1
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.endswith(":") and ":" not in line[:-1]:
            language = line[:-1].strip()
            continue
        match = LOC_ENTRY_START_RE.match(raw_line)
        if match is None:
            continue
        text_lines = [match.group("text")]
        while not _has_closing_quote("\n".join(text_lines)) and index < len(lines):
            text_lines.append(lines[index])
            index += 1
        entries.append(
            (
                match.group("key").strip(),
                _unescape_loc_text(_quoted_payload("\n".join(text_lines))),
            )
        )
    return {"language": language, "entries": sorted(entries)}


def _has_closing_quote(text: str) -> bool:
    escaped = False
    for char in text:
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == '"':
            return True
    return False


def _quoted_payload(text: str) -> str:
    escaped = False
    payload: list[str] = []
    for char in text:
        if escaped:
            payload.append("\\" + char)
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == '"':
            return "".join(payload)
        payload.append(char)
    if escaped:
        payload.append("\\")
    return "".join(payload)


def _unescape_loc_text(text: str) -> str:
    output: list[str] = []
    index = 0
    while index < len(text):
        if text[index] == "\\" and index + 1 < len(text):
            next_char = text[index + 1]
            output.append({"n": "\n", "t": "\t", "r": "\r"}.get(next_char, next_char))
            index += 2
        else:
            output.append(text[index])
            index += 1
    return "".join(output)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _artifact_bucket(artifact_path: str) -> str:
    parts = artifact_path.split("/")
    if len(parts) >= 2 and parts[0] == "common":
        return "/".join(parts[:2])
    if len(parts) >= 2 and parts[0] == "localisation":
        return "/".join(parts[:2])
    return parts[0]


def _normalize_idea_id(value: str) -> str:
    normalized = value.strip().upper()
    if normalized.startswith("IDEA_"):
        return normalized
    return f"IDEA_{normalized}"


if __name__ == "__main__":
    main()
