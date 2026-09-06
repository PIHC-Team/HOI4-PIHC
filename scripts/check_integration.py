"""Validate compiled tooltip dependencies and engine-required localization/UI paths.

Run after a build with --reference pointing at the installed Hearts of Iron IV.
This release gate is independent of release checksums and requires only stdlib.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

LANGUAGES = ("english", "simp_chinese")
TOKEN = re.compile(r'"(?:\\.|[^"\\])*"|#[^\n]*|[{}=<>!]+|[^\s{}=<>!#"]+')
ENTRY = re.compile(r'^\s*([^\s:#]+):\d*\s*"(.*)"\s*$', re.MULTILINE)
FIELDS = {"custom_effect_tooltip", "custom_modifier_tooltip", "custom_cost_text", "tooltip"}


def localization(root: Path, language: str) -> dict[str, str]:
    result = {}
    for path in sorted((root / "localisation").rglob(f"*_l_{language}.yml")):
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        if not re.search(rf"^\s*l_{language}:\s*$", text, re.MULTILINE):
            continue
        result.update(ENTRY.findall(text))
    return result


def tooltip_references(root: Path) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for directory in ("common", "events"):
        for path in sorted((root / directory).rglob("*.txt")):
            tokens = [t for t in TOKEN.findall(path.read_text(encoding="utf-8-sig")) if not t.startswith("#")]
            for i, token in enumerate(tokens[:-2]):
                if token not in FIELDS or tokens[i + 1] != "=":
                    continue
                key = tokens[i + 2].strip('"')
                # Dynamic substitutions and literal sentences are not localization identifiers.
                if re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*", key) and key not in {"yes", "no"}:
                    result.setdefault(key, []).append(path.relative_to(root).as_posix())
    return result


def check(root: Path, reference: Path) -> dict:
    errors = []
    refs = tooltip_references(root)
    for language in LANGUAGES:
        available = localization(reference, language) | localization(root, language)
        for key, paths in refs.items():
            if key not in available:
                errors.append(f"Missing {language} tooltip {key}: {paths[0]}")
    # These aggregate tables must shadow vanilla by path, not merely repeat its keys elsewhere.
    for language in (*LANGUAGES, "russian"):
        for table in ("state_names", "victory_points"):
            name = f"{table}_l_{language}.yml"
            path = root / "localisation" / language / name
            if not path.is_file():
                errors.append(f"Missing direct localization table: {path.relative_to(root)}")
            for obsolete in (root / "localisation/replace" / language / name, root / "localisation/replace" / name):
                if obsolete.exists():
                    errors.append(f"Obsolete duplicate table: {obsolete.relative_to(root)}")
    gui = root / "interface/frontendgamesetupview.gui"
    if gui.exists():
        text = gui.read_text(encoding="utf-8-sig")
        for name in ("country_entry", "country_entry_medium", "country_entry_mini"):
            match = re.search(r'containerWindowType\s*=\s*{\s*name\s*=\s*"' + name + '"', text)
            if match is None:
                errors.append(f"Missing country selection entry: {name}")
                continue
            start = text.index("{", match.start())
            depth = 0
            end = start
            for end in range(start, len(text)):
                depth += (text[end] == "{") - (text[end] == "}")
                if depth == 0:
                    break
            if not re.search(r'name\s*=\s*"new_content"', text[start:end]):
                errors.append(f"Missing engine-required new_content widget in {name}")
    return {"tooltip_keys": len(refs), "languages": list(LANGUAGES), "errors": errors}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not (args.reference / "localisation").is_dir() or not (args.output / "descriptor.mod").is_file():
        parser.error("Expected a compiled mod and a game reference with localization files")
    result = check(args.output, args.reference)
    print(
        json.dumps(result, ensure_ascii=False, indent=2)
        if args.json
        else f"Integration check: {result['tooltip_keys']} tooltip keys; {len(result['errors'])} errors."
    )
    if result["errors"]:
        if not args.json:
            print("\n".join(result["errors"]))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
