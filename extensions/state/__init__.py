"""PIHC3 state Entity and aggregate localization compiler."""

from __future__ import annotations

from pathlib import Path

import heavenbase as hb

from paradev.build import (
    Artifact,
    BuildContext,
    Collection,
    LocalizationEntry,
    Module,
    ModuleSourceBundle,
    SimpleSourceFamily,
    Slot,
)


class PIHC3State(hb.Entity):
    """One independently editable PIHC3 map state."""

    identifier = "pihc3-state"
    title = hb.field(hb.ShortText).default("").desc("Preferred-language state name stored in this module's main.loc.")
    state_id = hb.field(hb.Integer).desc("Numeric HoI4 state id; this is derived from the module folder id.")
    family = "state"
    resource_slots = (
        Slot("def", "def.txt", required=True, kind="pdx"),
        Slot("loc", "**/*.loc", many=True, kind="loc"),
    )
    compilation_hooks = ("normalize", "check", "emit")

    @classmethod
    def build_family(cls) -> "PIHC3StateFamily":
        """Return the state compiler."""

        return PIHC3StateFamily()


class PIHC3StateFamily(SimpleSourceFamily):
    """Compile states while aggregating module-owned names for HoI4."""

    replaces_registered_family = True
    source_form_field_hints = {
        "provinces": {
            "label": {
                "default": "Provinces",
                "zh": "省份",
            },
            "description": {
                "default": "Province ids inside this State, one per line.",
                "zh": "属于该地区的省份 ID，每行一个。",
            },
            "control": "integer-list",
            "columns": 1,
            "minimum": 1,
        },
        "victory_points": {
            "label": {
                "default": "Victory points",
                "zh": "胜利点",
            },
            "description": {
                "default": "One province id and victory-point score per row.",
                "zh": "每行填写一个省份 ID 和对应的胜利点分值。",
            },
            "control": "integer-list",
            "columns": 2,
            "minimum": 0,
        },
    }

    def __init__(self) -> None:
        super().__init__(
            family=PIHC3State.family,
            pdx_path_template="history/states/{object_id}.txt",
            source_slots=PIHC3State.resource_slots,
            required_loc_keys=("STATE_{object_id}",),
            title_loc_keys=("STATE_{object_id}",),
        )

    def emit(
        self,
        ctx: BuildContext,
        modules: tuple[Module, ...],
        collections: tuple[Collection, ...],
    ) -> tuple[Artifact, ...]:
        """Emit state definitions plus one game-facing name file per language."""

        artifacts = list(super().emit(ctx, modules, collections))
        entries_by_output: dict[tuple[str, str], list[LocalizationEntry]] = {}
        inputs_by_output: dict[tuple[str, str], list[Path]] = {}
        module_ids_by_output: dict[tuple[str, str], set[str]] = {}
        for module in sorted(modules, key=lambda item: item.module_id):
            bundle = _module_bundle(module)
            for entry in bundle.loc_entries:
                output_name = _localization_output_name(entry)
                output_key = (output_name, entry.language)
                entries_by_output.setdefault(output_key, []).append(entry)
                source = Path(bundle.root) / entry.source_path
                inputs = inputs_by_output.setdefault(output_key, [])
                if source not in inputs:
                    inputs.append(source)
                module_ids_by_output.setdefault(output_key, set()).add(module.module_id)
        for (output_name, language), entries in sorted(entries_by_output.items()):
            module_ids = sorted(module_ids_by_output[(output_name, language)])
            artifacts.append(
                Artifact(
                    path=(f"localisation/{language.removeprefix('l_')}/" f"{output_name}_{language}.yml"),
                    artifact_type="loc",
                    owner=f"project:{ctx.project_id}",
                    inputs=tuple(inputs_by_output[(output_name, language)]),
                    metadata={
                        "family": self.family,
                        "language": language,
                        "module_ids": module_ids,
                        "source_slot": "loc",
                    },
                    payload=tuple(sorted(entries, key=lambda entry: entry.key)),
                )
            )
        return tuple(artifacts)


def _localization_output_name(entry: LocalizationEntry) -> str:
    if entry.key.startswith("STATE_"):
        return "state_names"
    if entry.key.startswith("VICTORY_POINTS_"):
        return "victory_points"
    raise ValueError(f"State localization key {entry.key!r} is not owned by a state output.")


def _module_bundle(module: Module) -> ModuleSourceBundle:
    if isinstance(module.payload, ModuleSourceBundle):
        return module.payload
    raise ValueError(f"State module {module.module_id!r} must carry a ModuleSourceBundle payload.")


def build_family() -> PIHC3StateFamily:
    """HeavenBase Registry target for the state compiler."""

    return PIHC3State.build_family()
