"""PIHC3 strategic-region Entity and aggregate localization compiler."""

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


class PIHC3StrategicRegionModule(hb.Entity):
    """One independently editable PIHC3 strategic region."""

    identifier = "pihc3-strategic-region-module"
    title = hb.field(hb.ShortText).default("").desc("Preferred-language region name stored in this module's main.loc.")
    region_id = hb.field(hb.Integer).desc("Numeric HoI4 strategic-region id derived from the module folder id.")
    family = "strategic_region"
    resource_slots = (
        Slot("def", "def.txt", required=True, kind="pdx"),
        Slot("loc", "**/*.loc", many=True, kind="loc"),
    )
    compilation_hooks = ("normalize", "check", "emit")

    @classmethod
    def build_family(cls) -> "PIHC3StrategicRegionFamily":
        """Return the strategic-region compiler."""

        return PIHC3StrategicRegionFamily()


class PIHC3StrategicRegionFamily(SimpleSourceFamily):
    """Compile regions while aggregating module-owned names for HoI4."""

    replaces_registered_family = True
    source_form_field_hints = {
        "provinces": {
            "label": {
                "default": "Provinces",
                "zh": "省份",
            },
            "description": {
                "default": "Province ids inside this Strategic Region, one per line.",
                "zh": "属于该战略区域的省份 ID，每行一个。",
            },
            "control": "integer-list",
            "columns": 1,
            "minimum": 1,
        },
    }

    def __init__(self) -> None:
        super().__init__(
            family=PIHC3StrategicRegionModule.family,
            source_slots=PIHC3StrategicRegionModule.resource_slots,
            pdx_path_template="map/strategicregions/{object_id}.txt",
            required_loc_keys=("STRATEGICREGION_{object_id}",),
            title_loc_keys=("STRATEGICREGION_{object_id}",),
        )

    def emit(
        self,
        ctx: BuildContext,
        modules: tuple[Module, ...],
        collections: tuple[Collection, ...],
    ) -> tuple[Artifact, ...]:
        """Emit region definitions plus one game-facing name file per language."""

        artifacts = list(super().emit(ctx, modules, collections))
        entries_by_language: dict[str, list[LocalizationEntry]] = {}
        inputs_by_language: dict[str, list[Path]] = {}
        module_ids_by_language: dict[str, set[str]] = {}
        for module in sorted(modules, key=lambda item: item.module_id):
            bundle = _module_bundle(module)
            for entry in bundle.loc_entries:
                entries_by_language.setdefault(entry.language, []).append(entry)
                source = Path(bundle.root) / entry.source_path
                inputs = inputs_by_language.setdefault(entry.language, [])
                if source not in inputs:
                    inputs.append(source)
                module_ids_by_language.setdefault(entry.language, set()).add(module.module_id)
        for language, entries in sorted(entries_by_language.items()):
            artifacts.append(
                Artifact(
                    path=(f"localisation/{language.removeprefix('l_')}/" f"strategic_region_names_{language}.yml"),
                    artifact_type="loc",
                    owner=f"project:{ctx.project_id}",
                    inputs=tuple(inputs_by_language[language]),
                    metadata={
                        "family": self.family,
                        "language": language,
                        "module_ids": sorted(module_ids_by_language[language]),
                        "source_slot": "loc",
                    },
                    payload=tuple(sorted(entries, key=lambda entry: entry.key)),
                )
            )
        return tuple(artifacts)


def _module_bundle(module: Module) -> ModuleSourceBundle:
    if isinstance(module.payload, ModuleSourceBundle):
        return module.payload
    raise ValueError("Strategic-region module " f"{module.module_id!r} must carry a ModuleSourceBundle payload.")


def build_family() -> PIHC3StrategicRegionFamily:
    """Return the Registry compiler owned by this Entity extension."""

    return PIHC3StrategicRegionModule.build_family()


__all__ = [
    "PIHC3StrategicRegionFamily",
    "PIHC3StrategicRegionModule",
    "build_family",
]
