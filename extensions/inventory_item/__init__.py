"""PIHC3 compact inventory-item Entity and generated-helper compiler."""

from __future__ import annotations

import heavenbase as hb
from heavenbase.utils import load_txt, pj
from paradev.build import (
    Artifact,
    BuildContext,
    Collection,
    Diagnostic,
    LocalizationEntry,
    Module,
    ModuleSourceBundle,
    SimpleSourceFamily,
    Slot,
)

from .definition import (
    INVENTORY_ITEM_DEFINITION_PATH,
    InventoryItemDefinition,
    generated_inventory_localization_entries,
    inventory_effects_block,
    inventory_item_definition_source_form,
    inventory_triggers_block,
    is_generated_inventory_localization_key,
    load_inventory_item_definition,
)

INVENTORY_ITEM_ENTITY_ID = "pihc3-inventory-item"
INVENTORY_ITEM_FAMILY = "inventory_item"
INVENTORY_ITEM_SOURCE_SLOTS = (
    Slot(
        name="definition",
        match=INVENTORY_ITEM_DEFINITION_PATH,
        required=True,
    ),
    Slot(
        name="loc",
        match="**/*.loc",
        kind="loc",
        many=True,
    ),
    Slot(
        name="icon",
        match="icons/*",
        kind="copy",
        many=True,
        authoring_path="icons/{filename}",
    ),
)


class InventoryItem(hb.Entity):
    """PIHC3 inventory item with its authoring and compilation contract."""

    identifier = INVENTORY_ITEM_ENTITY_ID

    item_id = hb.field(hb.ShortText).desc("Stable inventory item identifier.")
    title = hb.field(hb.ShortText).default("").desc("Preferred-language display title.")
    description = (
        hb.field(hb.LongText).default("").desc("Preferred-language description.")
    )
    language = (
        hb.field(hb.ShortText).default("en").desc("Preferred authoring language.")
    )
    helper_quantities = (
        hb.field(hb.ShortText)
        .default("1")
        .desc("Compact quantities/ranges used to generate all helper scripts.")
    )
    localization = (
        hb.field(hb.Json)
        .default({})
        .desc("Localized item strings keyed by language and localization key.")
    )
    icons = hb.field(hb.Json).default([]).desc("Module-relative icon resource paths.")

    family = INVENTORY_ITEM_FAMILY
    resource_slots = INVENTORY_ITEM_SOURCE_SLOTS
    compilation_hooks = ("normalize", "check", "emit")

    @classmethod
    def build_family(cls) -> PIHC3InventoryItemFamily:
        """Return the build compiler declared by this Entity type."""

        return PIHC3InventoryItemFamily()


class PIHC3InventoryItemFamily(SimpleSourceFamily):
    """Generate PIHC3 inventory helpers from one compact item definition."""

    generated_outputs = (
        {
            "artifact_type": "pdx",
            "owner_kinds": ("module",),
            "target_root": "output",
        },
        {
            "artifact_type": "loc",
            "owner_kinds": ("module",),
            "target_root": "output",
        },
    )

    def __init__(self) -> None:
        super().__init__(
            family=InventoryItem.family,
            source_slots=InventoryItem.resource_slots,
            sprite_slots=("icon",),
            required_loc_keys=(
                "INVENTORY_ITEM_{object_id}",
                "INVENTORY_ITEM_{object_id}_DESC",
            ),
            loc_path_template="localisation/{language_folder}/INVENTORY_ITEM_{object_id}_{language}.yml",
            copy_path_template="gfx/interface/inventory_items/{source_name}",
            sprite_gfx_path_template="interface/PIHC3_inventory_items.gfx",
            sprite_name_template="GFX_{source_stem}",
        )

    def source_form(
        self,
        *,
        module_id: str,
        relative_path: str,
        text: str,
    ) -> dict[str, object] | None:
        """Return the guided form for one compact inventory definition."""

        if relative_path != INVENTORY_ITEM_DEFINITION_PATH:
            return None
        definition = load_inventory_item_definition(
            text,
            label=f"{module_id}/{relative_path}",
        )
        return inventory_item_definition_source_form(definition)

    def validate_source_text(
        self,
        *,
        module_id: str,
        relative_path: str,
        text: str,
    ) -> None:
        """Reject malformed compact definitions before a draft write."""

        if relative_path == INVENTORY_ITEM_DEFINITION_PATH:
            load_inventory_item_definition(
                text,
                label=f"{module_id}/{relative_path}",
            )

    def check(
        self,
        ctx: BuildContext,
        modules: tuple[Module, ...],
        collections: tuple[Collection, ...],
    ) -> tuple[Diagnostic, ...]:
        """Validate compact definitions and compiler-owned localization keys."""

        diagnostics = list(super().check(ctx, modules, collections))
        for module in modules:
            try:
                _module_definition(module)
            except (OSError, TypeError, ValueError) as error:
                diagnostics.append(
                    Diagnostic(
                        code="inventory_item.invalid_definition",
                        message=str(error),
                        family=self.family,
                        module_id=module.module_id,
                        slot="definition",
                        source_path=INVENTORY_ITEM_DEFINITION_PATH,
                    )
                )
            object_id = _module_object_id(module)
            for entry in _module_bundle(module).loc_entries:
                if not is_generated_inventory_localization_key(object_id, entry.key):
                    continue
                diagnostics.append(
                    Diagnostic(
                        code="inventory_item.authored_generated_localization",
                        message=(
                            f"Inventory item {module.module_id!r} localization key "
                            f"{entry.key!r} is generated from item.json and the item title."
                        ),
                        family=self.family,
                        module_id=module.module_id,
                        slot="loc",
                        source_path=entry.source_path,
                    )
                )
        return tuple(diagnostics)

    def emit(
        self,
        ctx: BuildContext,
        modules: tuple[Module, ...],
        collections: tuple[Collection, ...],
    ) -> tuple[Artifact, ...]:
        """Emit generated helpers, compact localization, icons, and sprites."""

        artifacts = [
            artifact
            for artifact in super().emit(ctx, modules, collections)
            if artifact.artifact_type != "loc"
        ]
        for module in sorted(modules, key=lambda item: item.module_id):
            bundle = _module_bundle(module)
            object_id = _module_object_id(module)
            definition, definition_path = _module_definition(module)
            definition_input = pj(bundle.root, definition_path)
            artifacts.extend(
                (
                    Artifact(
                        path=(
                            "common/scripted_effects/"
                            f"PIHC_INVENTORY_ITEM_{object_id}.txt"
                        ),
                        artifact_type="pdx",
                        owner=f"module:{module.module_id}",
                        inputs=(definition_input,),
                        metadata={
                            "family": self.family,
                            "source_slot": "definition",
                            "helper_quantity_count": len(definition.helper_quantities),
                        },
                        payload=inventory_effects_block(
                            object_id,
                            definition.helper_quantities,
                        ),
                    ),
                    Artifact(
                        path=(
                            "common/scripted_triggers/"
                            f"PIHC_INVENTORY_ITEM_{object_id}.txt"
                        ),
                        artifact_type="pdx",
                        owner=f"module:{module.module_id}",
                        inputs=(definition_input,),
                        metadata={
                            "family": self.family,
                            "source_slot": "definition",
                            "helper_quantity_count": len(definition.helper_quantities),
                        },
                        payload=inventory_triggers_block(
                            object_id,
                            definition.helper_quantities,
                        ),
                    ),
                )
            )
            generated = generated_inventory_localization_entries(
                object_id,
                definition.helper_quantities,
                bundle.loc_entries,
                source_path=definition_path,
                module_id=module.module_id,
            )
            entries_by_language: dict[str, list[LocalizationEntry]] = {}
            for entry in (*bundle.loc_entries, *generated):
                entries_by_language.setdefault(entry.language, []).append(entry)
            localization_inputs = tuple(
                [definition_input]
                + sorted(
                    {pj(bundle.root, entry.source_path) for entry in bundle.loc_entries}
                )
            )
            for language, entries in sorted(entries_by_language.items()):
                artifacts.append(
                    Artifact(
                        path=(
                            f"localisation/{language.removeprefix('l_')}/"
                            f"INVENTORY_ITEM_{object_id}_{language}.yml"
                        ),
                        artifact_type="loc",
                        owner=f"module:{module.module_id}",
                        inputs=localization_inputs,
                        metadata={
                            "family": self.family,
                            "language": language,
                            "source_slot": "definition",
                        },
                        payload=tuple(sorted(entries, key=lambda entry: entry.key)),
                    )
                )
        return tuple(artifacts)


def _module_bundle(module: Module) -> ModuleSourceBundle:
    if isinstance(module.payload, ModuleSourceBundle):
        return module.payload
    raise ValueError(
        f"Inventory item module {module.module_id!r} must carry a ModuleSourceBundle payload."
    )


def _module_object_id(module: Module) -> str:
    value = module.metadata.get("object_id")
    if isinstance(value, str) and value:
        return value
    return module.module_id.rsplit("/", 1)[-1]


def _module_definition(module: Module) -> tuple[InventoryItemDefinition, str]:
    bundle = _module_bundle(module)
    paths = tuple(bundle.source_slots.get("definition", ()))
    if len(paths) != 1:
        raise ValueError(
            f"Inventory item {module.module_id!r} must own exactly one "
            f"{INVENTORY_ITEM_DEFINITION_PATH}."
        )
    relative_path = paths[0]
    text = load_txt(
        pj(bundle.root, relative_path),
        encoding="utf-8",
        strict=True,
    )
    return (
        load_inventory_item_definition(
            text,
            label=f"{module.module_id}/{relative_path}",
        ),
        relative_path,
    )


def build_family() -> PIHC3InventoryItemFamily:
    """Materialize the inventory-item compiler through HeavenBase."""

    return InventoryItem.build_family()


__all__ = [
    "INVENTORY_ITEM_ENTITY_ID",
    "INVENTORY_ITEM_FAMILY",
    "INVENTORY_ITEM_SOURCE_SLOTS",
    "InventoryItem",
    "PIHC3InventoryItemFamily",
    "build_family",
]
