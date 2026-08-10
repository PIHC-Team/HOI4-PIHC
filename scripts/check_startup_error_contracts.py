"""Check PIHC3 source/output contracts for known HOI4 startup errors."""

# heaven-style-scan: standalone-control-plane

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_ROOT = Path.home() / "Documents/Paradox Interactive/Hearts of Iron IV/mod/PIHC3"

EXPECTED_BUILDING_ENTITIES = (
    "building_air_facility",
    "building_cataract_dam_mountain",
    "building_commercial_nuclear_reactor",
    "building_land_facility",
    "building_naval_facility",
    "building_naval_headquarters",
    "building_naval_supply_hub",
    "building_nuclear_reactor_heavy_water",
)
EXPECTED_BUILDING_MESHES = (
    "building_air_facility",
    "building_air_facility_destroyed",
    "building_commercial_nuclear_reactor",
    "building_commercial_nuclear_reactor_destroyed",
    "building_land_facility",
    "building_land_facility_destroyed",
    "building_naval_facility",
    "building_naval_facility_destroyed",
    "building_naval_headquarters",
    "building_naval_supply_hub",
    "cataract_mountain_dam_destroyed_mesh",
    "cataract_mountain_dam_mesh",
)
REQUIRED_SYNCHRONIZED_DYNAMIC_TOKENS = ("generator_complex",)
REQUIRED_ARMY_HQ_SUBUNITS = ("hq_support_company", "hq_infantry")
REQUIRED_REPLACE_PATHS = (
    "common/achievements",
    "common/bookmarks",
    "common/buildings",
    "common/intelligence_agencies",
    "common/national_focus",
)
VANILLA_ACHIEVEMENTS_OVERRIDE_MARKER = "PIHC3 total conversion intentionally shadows the incompatible vanilla achievements file."
UNAVAILABLE_SPECIAL_PROJECT_MODIFIERS = (
    "sp_nuclear_bomb_speed_factor",
    "sp_thermo_nuclear_bomb_speed_factor",
)

CLICK_SOUND_RE = re.compile(r"^\s*clicksound\s*=\s*click\s*(?:#.*)?$", re.MULTILINE)
LANDMARK_REPAIR_TOKEN = "@landmark_repair_speed_factor"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT, help="PIHC3 project root.")
    parser.add_argument(
        "--output-root",
        type=Path,
        default=None,
        help=f"Compiled PIHC3 output root. Defaults to no output checks; common default is {DEFAULT_OUTPUT_ROOT}.",
    )
    args = parser.parse_args()

    errors: list[str] = []
    check_source(args.project_root, errors)
    if args.output_root is not None:
        check_output(args.output_root, errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
    print("PIHC3 startup error contracts passed.")


def check_source(project_root: Path, errors: list[str]) -> None:
    module_root = project_root / "src" / "modules"
    check_click_sounds(module_root, errors, label="source")
    check_hidden_bookmark_source(project_root, errors)
    check_landmark_repair_tokens(module_root, errors, label="source")
    check_unavailable_special_project_modifiers(module_root, errors, label="source")
    check_vanilla_achievements_override(
        module_directory(module_root, "game_asset", "GAME_ASSET_COMMON_ACHIEVEMENTS") / "common" / "achievements.txt",
        errors,
        label="source",
    )
    check_map_adjacencies(
        module_directory(module_root, "game_asset", "GAME_ASSET_MAP_ADJACENCIES") / "map" / "adjacencies.csv",
        errors,
        label="source",
    )
    check_building_entities(
        module_directory(module_root, "game_asset", "GAME_ASSET_GFX_ENTITIES_BUILDINGS_ASSET") / "gfx" / "entities" / "buildings.asset",
        errors,
        label="source",
    )
    check_building_meshes(
        module_directory(module_root, "game_asset", "GAME_ASSET_GFX_ENTITIES_BUILDINGS_GFX") / "gfx" / "entities" / "buildings.gfx",
        errors,
        label="source",
    )
    check_synchronized_dynamic_tokens(
        module_directory(module_root, "common_data", "COMMON_DATA_SYNCHRONIZED_DYNAMIC_TOKENS") / "common" / "synchronized_dynamic_tokens" / "tokens.txt",
        errors,
        label="source",
    )
    check_army_hq_contracts(
        module_directory(module_root, "unit", "UNIT_UNITS_HQ_SUPPORT") / "common" / "units" / "hq_support.txt",
        module_directory(module_root, "general_history", "GENERAL_HISTORY_GENERAL_TAOG_HQ_TEMPLATE") / "history" / "general" / "taog_hq_template.txt",
        module_directory(module_root, "ai_config", "AI_CONFIG_AI_TEMPLATES_HQ_SUPPORT") / "common" / "ai_templates" / "hq_support.txt",
        errors,
        label="source",
    )
    check_focus_defaults(project_root / "src" / "collections" / "focus", errors)


def check_output(output_root: Path, errors: list[str]) -> None:
    if not output_root.is_dir():
        errors.append(f"compiled output root does not exist: {output_root}")
        return
    check_click_sounds(output_root, errors, label="compiled output")
    check_hidden_bookmark_output(output_root, errors)
    check_landmark_repair_tokens(output_root, errors, label="compiled output")
    check_unavailable_special_project_modifiers(output_root, errors, label="compiled output")
    check_vanilla_achievements_override(output_root / "common" / "achievements.txt", errors, label="compiled output")
    check_map_adjacencies(output_root / "map" / "adjacencies.csv", errors, label="compiled output")
    check_building_entities(output_root / "gfx" / "entities" / "buildings.asset", errors, label="compiled output")
    check_building_meshes(output_root / "gfx" / "entities" / "buildings.gfx", errors, label="compiled output")
    check_synchronized_dynamic_tokens(
        output_root / "common" / "synchronized_dynamic_tokens" / "tokens.txt",
        errors,
        label="compiled output",
    )
    check_army_hq_contracts(
        output_root / "common" / "units" / "hq_support.txt",
        output_root / "history" / "general" / "taog_hq_template.txt",
        output_root / "common" / "ai_templates" / "hq_support.txt",
        errors,
        label="compiled output",
    )
    check_generic_focus_filename(output_root / "common" / "national_focus", errors)
    check_generic_focus_id_order(
        first_existing(output_root / "common" / "national_focus", ("GENERIC.txt", "generic.txt")),
        errors,
        label="compiled output",
    )
    check_descriptor_replace_paths(output_root, errors)


def check_click_sounds(root: Path, errors: list[str], *, label: str) -> None:
    bad_paths: list[str] = []
    for path in text_files(root, suffixes=(".gfx", ".gui")):
        if CLICK_SOUND_RE.search(path.read_text(encoding="utf-8", errors="ignore")):
            bad_paths.append(format_path(path))
    if bad_paths:
        errors.append(f"{label} still references missing sound effect 'click': {', '.join(bad_paths)}")


def check_hidden_bookmark_source(project_root: Path, errors: list[str]) -> None:
    bookmark_root = project_root / "src" / "modules" / "bookmark"
    modules = tuple(path for path in bookmark_root.iterdir() if path.is_dir() and (path / "def.txt").is_file())
    active_ids = sorted(module_id(path) for path in modules if not module_is_inactive(path))
    if active_ids != ["PIHC"]:
        errors.append(f"expected only the release bookmark to be active, got: {active_ids}")
    hidden = next((path for path in modules if module_id(path) == "PIHC_DIE_NEBENWELT"), None)
    if hidden is None or not module_is_inactive(hidden):
        errors.append("future-dev bookmark must exist with `inactive: true` metadata")


def check_hidden_bookmark_output(output_root: Path, errors: list[str]) -> None:
    bookmark_root = output_root / "common" / "bookmarks"
    if not bookmark_root.is_dir():
        errors.append(f"compiled bookmark directory is missing: {bookmark_root}")
        return
    bookmark_text = "\n".join(path.read_text(encoding="utf-8", errors="ignore") for path in bookmark_root.glob("*.txt"))
    bookmark_count = len(re.findall(r"^\s*bookmark\s*=\s*\{", bookmark_text, flags=re.MULTILINE))
    if bookmark_count != 1:
        errors.append(f"expected one compiled release bookmark, got {bookmark_count}")
    if "PIHC_DIE_NEBENWELT" in bookmark_text or "DIE_NEBENWELT" in bookmark_text:
        errors.append("compiled output still exposes the hidden PIHC_DIE_NEBENWELT bookmark")


def check_landmark_repair_tokens(root: Path, errors: list[str], *, label: str) -> None:
    bad_paths = [
        format_path(path) for path in text_files(root, suffixes=(".txt",)) if LANDMARK_REPAIR_TOKEN in path.read_text(encoding="utf-8", errors="ignore")
    ]
    if bad_paths:
        errors.append(f"{label} still contains unresolved {LANDMARK_REPAIR_TOKEN}: {', '.join(bad_paths)}")


def check_unavailable_special_project_modifiers(root: Path, errors: list[str], *, label: str) -> None:
    for token in UNAVAILABLE_SPECIAL_PROJECT_MODIFIERS:
        bad_paths = [format_path(path) for path in text_files(root, suffixes=(".txt",)) if token in path.read_text(encoding="utf-8", errors="ignore")]
        if bad_paths:
            errors.append(f"{label} still references unavailable special-project modifier {token}: {', '.join(bad_paths)}")


def check_vanilla_achievements_override(path: Path, errors: list[str], *, label: str) -> None:
    if not path.is_file():
        errors.append(f"{label} vanilla achievements override is missing: {format_path(path)}")
        return
    text = path.read_text(encoding="utf-8", errors="ignore")
    if VANILLA_ACHIEVEMENTS_OVERRIDE_MARKER not in text:
        errors.append(f"{label} vanilla achievements override misses its ownership marker: {format_path(path)}")
    active_lines = [line.strip() for line in text.splitlines() if line.strip() and not line.lstrip().startswith("#")]
    if active_lines:
        errors.append(f"{label} vanilla achievements override must remain comment-only: {format_path(path)}")


def check_map_adjacencies(path: Path, errors: list[str], *, label: str) -> None:
    if not path.is_file():
        errors.append(f"{label} map adjacencies are missing: {format_path(path)}")
        return
    invalid: list[str] = []
    with path.open(encoding="utf-8-sig", newline="") as stream:
        rows = csv.DictReader(stream, delimiter=";")
        for line_number, row in enumerate(rows, start=2):
            source = (row.get("From") or "").strip()
            if source == "-1":
                break
            target = (row.get("To") or "").strip()
            through = (row.get("Through") or "").strip()
            if (row.get("Type") or "").strip() == "sea" and through in {source, target}:
                invalid.append(f"line {line_number} ({source}->{target} through {through})")
    if invalid:
        errors.append(f"{label} map adjacencies use an endpoint as Through: {', '.join(invalid)}")


def check_building_entities(path: Path, errors: list[str], *, label: str) -> None:
    if not path.is_file():
        errors.append(f"{label} building entity asset is missing: {format_path(path)}")
        return
    text = path.read_text(encoding="utf-8", errors="ignore")
    missing = [name for name in EXPECTED_BUILDING_ENTITIES if f'name = "{name}"' not in text]
    if missing:
        errors.append(f"{label} building entity asset misses: {', '.join(missing)}")


def check_building_meshes(path: Path, errors: list[str], *, label: str) -> None:
    if not path.is_file():
        errors.append(f"{label} building mesh definitions are missing: {format_path(path)}")
        return
    text = path.read_text(encoding="utf-8", errors="ignore")
    missing = [name for name in EXPECTED_BUILDING_MESHES if f'name = "{name}"' not in text]
    if missing:
        errors.append(f"{label} building mesh definitions miss: {', '.join(missing)}")


def check_synchronized_dynamic_tokens(path: Path, errors: list[str], *, label: str) -> None:
    if not path.is_file():
        errors.append(f"{label} synchronized dynamic tokens are missing: {format_path(path)}")
        return
    tokens = {line.strip() for line in path.read_text(encoding="utf-8", errors="ignore").splitlines() if line.strip() and not line.lstrip().startswith("#")}
    missing = [token for token in REQUIRED_SYNCHRONIZED_DYNAMIC_TOKENS if token not in tokens]
    if missing:
        errors.append(f"{label} synchronized dynamic tokens miss: {', '.join(missing)}")


def check_army_hq_contracts(
    unit_path: Path,
    template_path: Path,
    ai_path: Path,
    errors: list[str],
    *,
    label: str,
) -> None:
    if not unit_path.is_file():
        errors.append(f"{label} Army HQ subunit definitions are missing: {format_path(unit_path)}")
        return
    if not template_path.is_file():
        errors.append(f"{label} default Army HQ template is missing: {format_path(template_path)}")
        return
    if not ai_path.is_file():
        errors.append(f"{label} Army HQ AI template is missing: {format_path(ai_path)}")
        return

    unit_text = unit_path.read_text(encoding="utf-8", errors="ignore")
    missing_subunits = [subunit for subunit in REQUIRED_ARMY_HQ_SUBUNITS if f"{subunit} = {{" not in unit_text]
    if missing_subunits:
        errors.append(f"{label} Army HQ definitions miss: {', '.join(missing_subunits)}")
    for field in ("allow_in_army_hq = yes", "allow_in_non_army_hq = no"):
        if field not in unit_text:
            errors.append(f"{label} Army HQ definitions miss required field: {field}")
    if not re.search(r'required_dlc\s*=\s*\{\s*"Thunder at Our Gates"\s*\}', unit_text):
        errors.append(f'{label} Army HQ definitions miss required DLC: "Thunder at Our Gates"')
    if "ARCHETYPE_INFANTRY" not in unit_text:
        errors.append(f"{label} Army HQ definitions do not use the PIHC3 infantry equipment archetype")
    for vanilla_equipment in ("infantry_equipment", "support_equipment", "motorized_equipment"):
        if re.search(rf"^\s*{vanilla_equipment}\s*=", unit_text, re.MULTILINE):
            errors.append(f"{label} Army HQ definitions reference unavailable equipment: {vanilla_equipment}")

    template_text = template_path.read_text(encoding="utf-8", errors="ignore")
    for field in (
        "every_possible_country = {",
        'has_dlc = "Thunder at Our Gates"',
        'localization_key = "ARMY_HQ_TEMPLATE_NAME"',
        "template_counter = 121",
        "is_army_hq = yes",
        "hq_infantry = {",
        "hq_support_company = {",
    ):
        if field not in template_text:
            errors.append(f"{label} default Army HQ template misses required field: {field}")

    ai_text = ai_path.read_text(encoding="utf-8", errors="ignore")
    for field in (
        "hq_generic = {",
        "role = hq_role",
        "hq_default = {",
        "hq_support_company = 1",
        "hq_infantry = 2",
    ):
        if field not in ai_text:
            errors.append(f"{label} Army HQ AI template misses required field: {field}")


def check_focus_defaults(focus_root: Path, errors: list[str]) -> None:
    default_focuses = sorted(
        module_id(path.parent)
        for path in focus_root.glob("*/def.txt")
        if re.search(r"^\s*default\s*=\s*yes\s*$", path.read_text(encoding="utf-8", errors="ignore"), re.MULTILINE)
    )
    if default_focuses != ["generic"]:
        errors.append(f"expected generic to be the only default focus-tree collection, got: {default_focuses}")
    generic_root = next((path for path in focus_root.iterdir() if path.is_dir() and module_id(path) == "generic"), None)
    if generic_root is None:
        errors.append("source generic focus-tree collection is missing")
        return
    check_generic_focus_id_order(generic_root / "def.txt", errors, label="source")


def check_generic_focus_filename(root: Path, errors: list[str]) -> None:
    if not root.is_dir():
        errors.append(f"compiled national focus directory is missing: {format_path(root)}")
        return
    names = {path.name for path in root.glob("*.txt")}
    if "generic.txt" not in names:
        errors.append("compiled generic focus must be emitted as common/national_focus/generic.txt")
    if "GENERIC.txt" in names:
        errors.append("compiled generic focus must not be emitted as common/national_focus/GENERIC.txt")


def check_generic_focus_id_order(path: Path | None, errors: list[str], *, label: str) -> None:
    if path is None or not path.is_file():
        errors.append(f"{label} generic focus tree is missing")
        return
    text = path.read_text(encoding="utf-8", errors="ignore")
    id_match = re.search(r"^\s*id\s*=\s*generic_focus\s*$", text, re.MULTILINE)
    default_match = re.search(r"^\s*default\s*=\s*yes\s*$", text, re.MULTILINE)
    if id_match is None:
        errors.append(f"{label} generic focus tree misses id = generic_focus: {format_path(path)}")
        return
    if default_match is None:
        errors.append(f"{label} generic focus tree misses default = yes: {format_path(path)}")
        return
    if default_match.start() < id_match.start():
        errors.append(f"{label} generic focus tree declares default = yes before id = generic_focus: {format_path(path)}")


def check_descriptor_replace_paths(output_root: Path, errors: list[str]) -> None:
    descriptor_paths = [output_root / "descriptor.mod", output_root.parent / "PIHC3.mod"]
    for descriptor in descriptor_paths:
        if not descriptor.is_file():
            errors.append(f"compiled descriptor is missing: {format_path(descriptor)}")
            continue
        text = descriptor.read_text(encoding="utf-8", errors="ignore")
        missing = [path for path in REQUIRED_REPLACE_PATHS if f'replace_path="{path}"' not in text]
        if missing:
            errors.append(f"{format_path(descriptor)} misses replace_path entries: {', '.join(missing)}")


def text_files(root: Path, *, suffixes: tuple[str, ...]) -> list[Path]:
    if not root.exists():
        return []
    return sorted(path for path in root.rglob("*") if path.is_file() and path.suffix.lower() in suffixes)


def first_existing(root: Path, filenames: tuple[str, ...]) -> Path | None:
    for filename in filenames:
        path = root / filename
        if path.is_file():
            return path
    return None


def module_id(path: Path) -> str:
    return path.name.partition(" - ")[0]


def module_directory(module_root: Path, family: str, object_id: str) -> Path:
    family_root = module_root / family
    matches = [path for path in family_root.glob(f"{object_id} - *") if path.is_dir()]
    if len(matches) == 1:
        return matches[0]
    return family_root / object_id


def module_is_inactive(path: Path) -> bool:
    metadata = path / "meta.yaml"
    if not metadata.is_file():
        return False
    return bool(re.search(r"^\s*inactive\s*:\s*true\s*$", metadata.read_text(encoding="utf-8"), re.MULTILINE | re.IGNORECASE))


def format_path(path: Path) -> str:
    try:
        return path.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    main()
