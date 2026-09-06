"""Verify a compiled PIHC3 directory against the canonical release manifest.

This standalone verification command requires only Python's standard library.
"""

# heaven-style-scan: standalone-control-plane

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    """Check every expected game file and reject extra game content."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="Directory containing descriptor.mod.")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=PROJECT_ROOT / "docs/releases/unified-20260905-r2-files.json",
    )
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    expected = manifest["files"]
    errors: list[str] = []
    for name, digest in expected.items():
        path = args.output / name
        if path.is_symlink():
            errors.append(f"Symbolic link is not standalone: {name}")
        elif not path.is_file():
            errors.append(f"Missing: {name}")
        elif hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            errors.append(f"Changed: {name}")
    for root in manifest["game_directories"]:
        for path in (args.output / root).rglob("*"):
            if path.is_file() and path.relative_to(args.output).as_posix() not in expected:
                errors.append(f"Unexpected game file: {path.relative_to(args.output)}")
    if errors:
        for error in errors:
            print(error)
        raise SystemExit(1)
    print(f"Verified {len(expected):,} standalone game files for {manifest['release']}.")


if __name__ == "__main__":
    main()
