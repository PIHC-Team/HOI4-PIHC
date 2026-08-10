"""Project-local equipment aggregate family."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import ClassVar

import heavenbase as hb

from paradev.build import (
    Artifact,
    BuildContext,
    BuildRegistry,
    Collection,
    Diagnostic,
    Module,
    ModuleSourceBundle,
    SimpleSourceFamily,
    Slot,
)
from paradev.pdx import PDXBlock, PDXEntry, PDXScalar

_SOURCE_FORM_FIELD_HINTS = {
    "year": {
        "description": {
            "default": "Technology year used for equipment availability and progression.",
            "zh": "用于装备可用性和进度的科技年份。",
        }
    },
    "is_archetype": {
        "description": {
            "default": "Whether this definition is an equipment archetype.",
            "zh": "该定义是否为装备原型。",
        }
    },
    "active": {
        "description": {
            "default": "Whether this equipment is available to the game.",
            "zh": "该装备是否在游戏中可用。",
        }
    },
    "archetype": {
        "description": {
            "default": "Parent equipment archetype inherited by this variant.",
            "zh": "该变体继承的父级装备原型。",
        }
    },
    "build_cost_ic": {
        "description": {
            "default": "Industrial production cost for one unit of this equipment.",
            "zh": "生产一件该装备所需的工业成本。",
        }
    },
    "reliability": {
        "description": {
            "default": "Equipment reliability as a decimal proportion.",
            "zh": "以小数比例表示的装备可靠性。",
        }
    },
}


class EquipmentFamily:
    """Emit PIHC equipment definitions into one load-order-safe aggregate file."""

    family_kind: ClassVar[str] = "equipment_aggregate"
    family: ClassVar[str] = "equipment"
    output_path: ClassVar[str] = "common/units/equipment/zz_all_equipments.txt"
    loc_path_template: ClassVar[str] = "localisation/{language_folder}/{object_id}_{language}.yml"
    copy_path_template: ClassVar[str] = "{source_path}"
    source_slots: ClassVar[tuple[Slot, ...]] = (
        Slot(name="def", match="def.txt", kind="pdx", required=True),
        Slot(name="loc", match="**/*.loc", kind="loc", many=True),
        Slot(
            name="assets",
            match=r"^gfx/interface/equipments/.+\.dds$",
            regex=True,
            kind="copy",
            many=True,
            authoring_path="gfx/interface/equipments/{filename}",
        ),
        Slot(
            name="assets",
            match=r"^interface/equipments/.+\.gfx$",
            regex=True,
            kind="copy",
            many=True,
            authoring_path="interface/equipments/{filename}",
        ),
        Slot(
            name="assets",
            match=r"^interface/equipmentdesigner/.+\.gui$",
            regex=True,
            kind="copy",
            many=True,
            authoring_path="interface/equipmentdesigner/{filename}",
        ),
    )
    metadata_keys: ClassVar[tuple[str, ...]] = ()
    settings_keys: ClassVar[tuple[str, ...]] = ()
    settings_values: ClassVar[Mapping[str, tuple[str, ...]]] = {}
    required_settings: ClassVar[tuple[str, ...]] = ()
    required_loc_keys: ClassVar[tuple[str, ...]] = ("{object_id}", "{object_id}_desc")
    asset_constraints: ClassVar[Mapping[str, Mapping[str, object]]] = {}
    settings_normalizers: ClassVar[Mapping[str, object]] = {}
    source_form_field_hints: ClassVar[Mapping[str, Mapping[str, object]]] = (
        _SOURCE_FORM_FIELD_HINTS
    )

    def check(
        self,
        ctx: BuildContext,
        modules: tuple[Module, ...],
        collections: tuple[Collection, ...],
    ) -> tuple[Diagnostic, ...]:
        """Return localization, asset, and source-fragment diagnostics."""

        diagnostics = list(_sidecar_family().check(ctx, modules, collections))
        for module in modules:
            diagnostics.extend(_module_def_diagnostics(module))
        return tuple(diagnostics)

    def emit(
        self,
        ctx: BuildContext,
        modules: tuple[Module, ...],
        collections: tuple[Collection, ...],
    ) -> tuple[Artifact, ...]:
        """Emit sidecar artifacts and the aggregate equipment PDX file."""

        ordered = _ordered_modules(modules)
        artifacts: list[Artifact] = list(_sidecar_family().emit(ctx, ordered, collections))
        aggregate = _aggregate_artifact(ctx, ordered)
        if aggregate is not None:
            artifacts.append(aggregate)
        return tuple(artifacts)


def register(registry: BuildRegistry) -> BuildRegistry:
    """Register project-local PIHC3 equipment build family."""

    return registry.add(EquipmentFamily())


class PIHC3Equipment(hb.Entity):
    """PIHC3 equipment definition with owned sidecar and aggregate hooks."""

    identifier = "pihc3-equipment"

    equipment_id = hb.field(hb.ShortText).desc("Stable HoI4 equipment identifier.")
    title = hb.field(hb.ShortText).default("").desc("Preferred-language equipment name.")
    description = hb.field(hb.LongText).default("").desc("Preferred-language description.")
    definition = hb.field(hb.LongText).default("").desc("Equipment PDX definition.")
    localization = hb.field(hb.Json).default({}).desc("Localized equipment strings.")
    assets = hb.field(hb.Json).default([]).desc("Module-relative equipment asset paths.")

    family = EquipmentFamily.family
    resource_slots = EquipmentFamily.source_slots
    compilation_hooks = ("normalize", "check", "emit")
    # HeavenBase Entity annotations are logical fields; protocol metadata stays unannotated.
    source_form_field_hints = _SOURCE_FORM_FIELD_HINTS

    @classmethod
    def build_family(cls) -> EquipmentFamily:
        """Return the aggregate compiler owned by this Entity type."""

        return EquipmentFamily()


def _sidecar_family() -> SimpleSourceFamily:
    return SimpleSourceFamily(
        family=EquipmentFamily.family,
        loc_path_template=EquipmentFamily.loc_path_template,
        copy_path_template=EquipmentFamily.copy_path_template,
        source_slots=EquipmentFamily.source_slots,
        required_loc_keys=EquipmentFamily.required_loc_keys,
    )


def _aggregate_artifact(ctx: BuildContext, modules: tuple[Module, ...]) -> Artifact | None:
    entries: list[PDXEntry] = []
    inputs: list[Path] = []
    for module in modules:
        bundle = _module_bundle(module)
        object_id = _module_object_id(module)
        for source in bundle.pdx_sources:
            if source.slot != "def":
                continue
            module_entries = _module_def_entries(source.block, object_id)
            if not module_entries:
                continue
            entries.extend(entry.clone() for entry in module_entries)
            inputs.append(Path(bundle.root) / source.path)
    if not entries:
        return None
    return Artifact(
        path=EquipmentFamily.output_path,
        artifact_type="pdx",
        owner=f"project:{ctx.project_id}",
        inputs=tuple(inputs),
        metadata={"family": EquipmentFamily.family, "equipment_count": len(entries)},
        payload=PDXBlock.from_entries([PDXEntry.kv("equipments", PDXBlock.from_entries(entries))]),
    )


def _module_def_diagnostics(module: Module) -> tuple[Diagnostic, ...]:
    diagnostics: list[Diagnostic] = []
    object_id = _module_object_id(module)
    bundle = _module_bundle(module)
    for source in bundle.pdx_sources:
        if source.slot != "def":
            continue
        if _module_def_entries(source.block, object_id):
            continue
        diagnostics.append(
            Diagnostic(
                code="equipment.missing_definition",
                message=f"Equipment module {module.module_id} must define {object_id}.",
                severity="error",
                family=EquipmentFamily.family,
                module_id=module.module_id,
                slot="def",
                source_path=source.path,
            )
        )
    return tuple(diagnostics)


def _module_def_entries(block: PDXBlock, object_id: str) -> tuple[PDXEntry, ...]:
    wrapper = block.find("equipments")
    if wrapper is not None and isinstance(wrapper.val, PDXBlock):
        return tuple(entry for entry in wrapper.val.entries if entry.key_str == object_id)
    return tuple(entry for entry in block.entries if entry.key_str == object_id)


def _ordered_modules(modules: tuple[Module, ...]) -> tuple[Module, ...]:
    entries_by_id: dict[str, PDXEntry] = {}
    modules_by_id: dict[str, Module] = {}
    for module in modules:
        object_id = _module_object_id(module)
        entry = _first_module_entry(module, object_id)
        modules_by_id[object_id] = module
        if entry is not None:
            entries_by_id[object_id] = entry
    known_ids = set(modules_by_id)
    remaining = set(modules_by_id)
    deps_by_id = {object_id: _entry_dependencies(entries_by_id.get(object_id), known_ids) for object_id in modules_by_id}
    ordered: list[Module] = []
    while remaining:
        ready = [object_id for object_id in remaining if not deps_by_id[object_id] & remaining]
        if not ready:
            ordered.extend(modules_by_id[object_id] for object_id in sorted(remaining, key=lambda item: _module_sort_key(modules_by_id[item])))
            break
        for object_id in sorted(ready, key=lambda item: _module_sort_key(modules_by_id[item])):
            ordered.append(modules_by_id[object_id])
            remaining.remove(object_id)
    return tuple(ordered)


def _first_module_entry(module: Module, object_id: str) -> PDXEntry | None:
    bundle = _module_bundle(module)
    for source in bundle.pdx_sources:
        if source.slot != "def":
            continue
        entries = _module_def_entries(source.block, object_id)
        if entries:
            return entries[0]
    return None


def _entry_dependencies(entry: PDXEntry | None, known_ids: set[str]) -> set[str]:
    if entry is None or not isinstance(entry.val, PDXBlock):
        return set()
    deps: set[str] = set()
    for item in entry.val.entries:
        if item.key_str not in {"archetype", "parent"} or not isinstance(item.val, PDXScalar):
            continue
        value = str(item.val.val)
        if value in known_ids and value != entry.key_str:
            deps.add(value)
    return deps


def _module_bundle(module: Module) -> ModuleSourceBundle:
    if isinstance(module.payload, ModuleSourceBundle):
        return module.payload
    raise ValueError(f"Module {module.module_id!r} must carry a ModuleSourceBundle payload.")


def _module_object_id(module: Module) -> str:
    value = module.metadata.get("object_id")
    if isinstance(value, str) and value:
        return value
    return module.module_id.rsplit("/", 1)[-1]


def _module_sort_key(module: Module) -> tuple[int, str]:
    settings = module.metadata.get("settings")
    settings_map = settings if isinstance(settings, Mapping) else {}
    value = settings_map.get("legacy_order")
    if isinstance(value, int):
        return (value, _module_object_id(module))
    return (10**9, module.module_id)
