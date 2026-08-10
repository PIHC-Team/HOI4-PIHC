"""Project-local equipment designer module aggregate family."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import replace
from pathlib import Path
from typing import ClassVar

import heavenbase as hb

from paradev.build import (
    Artifact,
    BuildContext,
    BuildRegistry,
    Collection,
    Diagnostic,
    FamilyNormalizeResult,
    Module,
    ModuleSourceBundle,
    SimpleSourceFamily,
    Slot,
    SpriteType,
)
from paradev.pdx import PDXBlock, PDXEntry, PDXScalar


class EquipmentModuleFamily:
    """Emit PIHC equipment designer modules into HOI4 aggregate module files."""

    family_kind: ClassVar[str] = "equipment_module_aggregate"
    family: ClassVar[str] = "equipment_module"
    output_paths: ClassVar[dict[str, str]] = {
        "plane": "common/units/equipment/modules/00_plane_modules.txt",
        "tank": "common/units/equipment/modules/00_tank_modules.txt",
    }
    dlc_by_module_type: ClassVar[dict[str, str]] = {
        "plane": "By Blood Alone",
        "tank": "No Step Back",
    }
    loc_path_template: ClassVar[str] = "localisation/{language_folder}/{object_id}_{language}.yml"
    copy_path_template: ClassVar[str] = "gfx/interface/modules/{object_id}{source_suffix}"
    sprite_gfx_path: ClassVar[str] = "interface/PIHC3_equipment_modules.gfx"
    source_slots: ClassVar[tuple[Slot, ...]] = (
        Slot(name="def", match="def.txt", kind="pdx", required=True),
        Slot(name="loc", match="**/*.loc", kind="loc", many=True),
        Slot(
            name="icon",
            match="icon.png",
            kind="copy",
            authoring_path="{filename}",
        ),
        Slot(
            name="icon",
            match=r"^icon\.(dds|tga)$",
            regex=True,
            kind="copy",
            authoring_path="{filename}",
        ),
    )
    metadata_keys: ClassVar[tuple[str, ...]] = ()
    settings_keys: ClassVar[tuple[str, ...]] = ()
    settings_values: ClassVar[Mapping[str, tuple[str, ...]]] = {}
    required_settings: ClassVar[tuple[str, ...]] = ()
    required_loc_keys: ClassVar[tuple[str, ...]] = ("{object_id}",)
    asset_constraints: ClassVar[Mapping[str, Mapping[str, object]]] = {}
    settings_normalizers: ClassVar[Mapping[str, object]] = {}

    def normalize(
        self,
        ctx: BuildContext,
        modules: tuple[Module, ...],
        collections: tuple[Collection, ...],
    ) -> FamilyNormalizeResult:
        """Derive compiler routing from each module's authored category."""

        return FamilyNormalizeResult(modules=tuple(_module_with_inferred_settings(module) for module in modules))

    def check(
        self,
        ctx: BuildContext,
        modules: tuple[Module, ...],
        collections: tuple[Collection, ...],
    ) -> tuple[Diagnostic, ...]:
        """Return settings, localization, and source-fragment diagnostics."""

        diagnostics = list(_sidecar_family().check(ctx, modules, collections))
        for module in modules:
            diagnostics.extend(_module_def_diagnostics(module))
            diagnostics.extend(_module_routing_diagnostics(module))
        return tuple(diagnostics)

    def emit(
        self,
        ctx: BuildContext,
        modules: tuple[Module, ...],
        collections: tuple[Collection, ...],
    ) -> tuple[Artifact, ...]:
        """Emit sidecar artifacts and aggregate module PDX files."""

        ordered = tuple(sorted(modules, key=_module_sort_key))
        artifacts: list[Artifact] = list(_sidecar_family().emit(ctx, ordered, collections))
        for module_type, output_path in sorted(self.output_paths.items()):
            aggregate = _aggregate_artifact(ctx, ordered, module_type=module_type, output_path=output_path)
            if aggregate is not None:
                artifacts.append(aggregate)
        sprite_artifact = _sprite_artifact(ctx, ordered)
        if sprite_artifact is not None:
            artifacts.append(sprite_artifact)
        return tuple(artifacts)


def register(registry: BuildRegistry) -> BuildRegistry:
    """Register project-local PIHC3 equipment-module build family."""

    return registry.add(EquipmentModuleFamily())


class PIHC3EquipmentModule(hb.Entity):
    """PIHC3 equipment-designer module with its aggregate compiler contract."""

    identifier = "pihc3-equipment-module"

    module_id = hb.field(hb.ShortText).desc("Stable equipment module identifier.")
    category_id = hb.field(hb.ShortText).desc("Designer category receiving this module.")
    title = hb.field(hb.ShortText).default("").desc("Preferred-language module name.")
    definition = hb.field(hb.LongText).default("").desc("Equipment-module PDX definition.")
    localization = hb.field(hb.Json).default({}).desc("Localized equipment-module strings.")
    icon = hb.field(hb.ShortText).default("").desc("Module-relative icon resource path.")

    family = EquipmentModuleFamily.family
    resource_slots = EquipmentModuleFamily.source_slots
    compilation_hooks = ("normalize", "check", "emit")

    @classmethod
    def build_family(cls) -> EquipmentModuleFamily:
        """Return the aggregate compiler owned by this Entity type."""

        return EquipmentModuleFamily()


def _sidecar_family() -> SimpleSourceFamily:
    return SimpleSourceFamily(
        family=EquipmentModuleFamily.family,
        loc_path_template=EquipmentModuleFamily.loc_path_template,
        copy_path_template=EquipmentModuleFamily.copy_path_template,
        source_slots=EquipmentModuleFamily.source_slots,
        settings_keys=EquipmentModuleFamily.settings_keys,
        settings_values=EquipmentModuleFamily.settings_values,
        required_settings=EquipmentModuleFamily.required_settings,
        required_loc_keys=EquipmentModuleFamily.required_loc_keys,
    )


def _aggregate_artifact(
    ctx: BuildContext,
    modules: tuple[Module, ...],
    *,
    module_type: str,
    output_path: str,
) -> Artifact | None:
    entries = [_limit_entry(module_type)]
    inputs: list[Path] = []
    module_count = 0
    for module in modules:
        if _module_type(module) != module_type:
            continue
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
            module_count += len(module_entries)
    if module_count == 0:
        return None
    return Artifact(
        path=output_path,
        artifact_type="pdx",
        owner=f"project:{ctx.project_id}",
        inputs=tuple(inputs),
        metadata={
            "family": EquipmentModuleFamily.family,
            "module_type": module_type,
            "module_count": module_count,
        },
        payload=PDXBlock.from_entries([PDXEntry.kv("equipment_modules", PDXBlock.from_entries(entries))]),
    )


def _sprite_artifact(ctx: BuildContext, modules: tuple[Module, ...]) -> Artifact | None:
    sprites: list[SpriteType] = []
    inputs: list[Path] = []
    for module in modules:
        bundle = _module_bundle(module)
        object_id = _module_object_id(module)
        for source in bundle.copy_sources:
            if source.slot != "icon":
                continue
            texturefile = f"gfx/interface/modules/{object_id}{Path(source.path).suffix}"
            sprites.append(SpriteType(name=f"GFX_{object_id}", texturefile=texturefile))
            sprites.append(
                SpriteType(
                    name=f"GFX_EMI_{object_id}",
                    texturefile=texturefile,
                    properties={"legacy_lazy_load": False},
                )
            )
            inputs.append(Path(bundle.root) / source.path)
    if not sprites:
        return None
    return Artifact(
        path=EquipmentModuleFamily.sprite_gfx_path,
        artifact_type="sprite_gfx",
        owner=f"project:{ctx.project_id}",
        inputs=tuple(inputs),
        metadata={"family": EquipmentModuleFamily.family, "sprite_count": len(sprites)},
        payload=tuple(sprites),
    )


def _limit_entry(module_type: str) -> PDXEntry:
    return PDXEntry.kv(
        "limit",
        PDXBlock.from_entries([PDXEntry.kv("has_dlc", EquipmentModuleFamily.dlc_by_module_type[module_type])]),
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
                code="equipment_module.missing_definition",
                message=f"Equipment module {module.module_id} must define {object_id}.",
                severity="error",
                family=EquipmentModuleFamily.family,
                module_id=module.module_id,
                slot="def",
                source_path=source.path,
            )
        )
    return tuple(diagnostics)


def _module_routing_diagnostics(module: Module) -> tuple[Diagnostic, ...]:
    category_id = _module_category_id(module)
    if category_id is None:
        return (
            Diagnostic(
                code="equipment_module.missing_category",
                message=(f"Equipment module {module.module_id} must define a category " "inside def.txt."),
                severity="error",
                family=EquipmentModuleFamily.family,
                module_id=module.module_id,
                slot="def",
                source_path="def.txt",
            ),
        )
    module_type = _module_type(module)
    if module_type in EquipmentModuleFamily.output_paths:
        return ()
    return (
        Diagnostic(
            code="equipment_module.unknown_designer",
            message=(
                f"Equipment module {module.module_id} category {category_id!r} "
                "must start with pihc_plane_ or pihc_tank_, or declare an "
                "advanced settings.module_type override."
            ),
            severity="error",
            family=EquipmentModuleFamily.family,
            module_id=module.module_id,
            slot="def",
            source_path="def.txt",
        ),
    )


def _module_def_entries(block: PDXBlock, object_id: str) -> tuple[PDXEntry, ...]:
    wrapper = block.find("equipment_modules")
    if wrapper is not None and isinstance(wrapper.val, PDXBlock):
        return tuple(entry.clone() for entry in wrapper.val.entries if entry.key_str == object_id)
    return tuple(entry.clone() for entry in block.entries if entry.key_str == object_id)


def _module_with_inferred_settings(module: Module) -> Module:
    category_id = _module_category_id(module)
    if category_id is None:
        return module
    settings = module.metadata.get("settings")
    normalized_settings = dict(settings) if isinstance(settings, Mapping) else {}
    normalized_settings["category_id"] = category_id
    module_type = _module_type_for_category(category_id)
    if module_type is not None:
        normalized_settings["module_type"] = module_type
    metadata = dict(module.metadata)
    metadata["settings"] = normalized_settings
    payload = module.payload
    if isinstance(payload, ModuleSourceBundle):
        payload = replace(payload, metadata=dict(metadata))
    return replace(module, metadata=metadata, payload=payload)


def _module_category_id(module: Module) -> str | None:
    bundle = _module_bundle(module)
    object_id = _module_object_id(module)
    for source in bundle.pdx_sources:
        if source.slot != "def":
            continue
        for definition in _module_def_entries(source.block, object_id):
            if not isinstance(definition.val, PDXBlock):
                continue
            for entry in definition.val.entries:
                if entry.key_str == "category" and isinstance(entry.val, PDXScalar):
                    category_id = str(entry.val.val).strip()
                    return category_id or None
    return None


def _module_type_for_category(category_id: str) -> str | None:
    for module_type in EquipmentModuleFamily.output_paths:
        if category_id.startswith(f"pihc_{module_type}_"):
            return module_type
    return None


def _module_bundle(module: Module) -> ModuleSourceBundle:
    if isinstance(module.payload, ModuleSourceBundle):
        return module.payload
    raise ValueError(f"Module {module.module_id!r} must carry a ModuleSourceBundle payload.")


def _module_object_id(module: Module) -> str:
    value = module.metadata.get("object_id")
    if isinstance(value, str) and value:
        return value
    return module.module_id.rsplit("/", 1)[-1]


def _module_type(module: Module) -> str | None:
    settings = module.metadata.get("settings")
    settings_map = settings if isinstance(settings, Mapping) else {}
    value = settings_map.get("module_type")
    return value if isinstance(value, str) else None


def _module_sort_key(module: Module) -> tuple[str, str, str]:
    settings = module.metadata.get("settings")
    settings_map = settings if isinstance(settings, Mapping) else {}
    module_type = settings_map.get("module_type")
    category_id = settings_map.get("category_id")
    return (
        str(module_type or ""),
        str(category_id or ""),
        _module_object_id(module),
    )
