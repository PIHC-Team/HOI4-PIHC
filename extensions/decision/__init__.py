"""PIHC3 compiler overlay for the built-in decision family."""

from __future__ import annotations

from dataclasses import replace
from typing import ClassVar

from paradev.build import (
    Artifact,
    BuildContext,
    Collection,
    Diagnostic,
    FamilyNormalizeResult,
    Module,
    SimpleSourceFamily,
    Slot,
)
from paradev.games.hoi4 import DecisionFamily
from paradev.pdx import PDXBlock

DECISION_RESOURCE_SLOTS = (
    Slot("def", "def.txt", kind="pdx"),
    Slot("loc", "**/*.loc", many=True, kind="loc"),
    Slot("preview", "preview.png"),
    Slot(
        "compiled_assets",
        r"^gfx/interface/decisions/.*\.dds$",
        many=True,
        regex=True,
        kind="copy",
        authoring_path="gfx/interface/decisions/{filename}",
    ),
    Slot(
        "compiled_assets",
        r"^interface/decisions/.*\.gfx$",
        many=True,
        regex=True,
        kind="copy",
        authoring_path="interface/decisions/{filename}",
    ),
    Slot(
        "shared_pdx",
        r"^common/decisions/.*\.txt$",
        many=True,
        regex=True,
        kind="pdx",
    ),
)
DECISION_COLLECTION_RESOURCE_SLOTS = (
    Slot("def", "def.txt", kind="pdx"),
    Slot("loc", "**/*.loc", many=True, kind="loc"),
    Slot("preview", "preview.png"),
    Slot("icon", "icon.png"),
    Slot(
        "compiled_assets",
        r"^gfx/interface/decisions/.*\.dds$",
        many=True,
        regex=True,
        kind="copy",
        authoring_path="gfx/interface/decisions/{filename}",
    ),
    Slot(
        "compiled_assets",
        r"^interface/decisions/.*\.gfx$",
        many=True,
        regex=True,
        kind="copy",
        authoring_path="interface/decisions/{filename}",
    ),
)
DECISION_SOURCE_FORM_FIELD_HINTS = {
    "cost": {
        "description": {
            "default": "Political-power cost paid when this decision is taken.",
            "zh": "执行该决议时支付的政治点数。",
        }
    },
    "days_remove": {
        "description": {
            "default": "Number of days before the decision is removed automatically.",
            "zh": "该决议自动移除前的天数。",
        }
    },
    "fire_only_once": {
        "description": {
            "default": "Whether this decision may complete only once.",
            "zh": "该决议是否只能完成一次。",
        }
    },
    "icon": {
        "description": {
            "default": "Sprite identifier displayed for this decision.",
            "zh": "该决议显示的精灵标识。",
        }
    },
    "priority": {
        "description": {
            "default": "AI selection priority for this decision.",
            "zh": "AI 选择该决议时的优先级。",
        }
    },
}


class PIHC3DecisionFamily(DecisionFamily):
    """Compile decision modules, collections, and shared decision sources."""

    replaces_registered_family = True
    source_form_field_hints: ClassVar[dict[str, dict[str, object]]] = DECISION_SOURCE_FORM_FIELD_HINTS

    def __init__(self) -> None:
        super().__init__(
            family="decision",
            pdx_path_template="common/decisions/{collection_id}.txt",
            loc_path_template=("localisation/{language_folder}/{object_id}_{language}.yml"),
            copy_path_template="{source_path}",
            source_slots=DECISION_RESOURCE_SLOTS,
            collection_source_slots=DECISION_COLLECTION_RESOURCE_SLOTS,
        )

    def normalize(
        self,
        ctx: BuildContext,
        modules: tuple[Module, ...],
        collections: tuple[Collection, ...],
    ) -> FamilyNormalizeResult:
        """Infer authored decision collections from their definition blocks."""

        normalized = super().normalize(ctx, modules, collections)
        return FamilyNormalizeResult(
            modules=tuple(_with_inferred_collection(module) for module in normalized.modules),
            diagnostics=normalized.diagnostics,
        )

    def check(
        self,
        ctx: BuildContext,
        modules: tuple[Module, ...],
        collections: tuple[Collection, ...],
    ) -> tuple[Diagnostic, ...]:
        """Validate authored decision nodes without treating shared files as nodes."""

        authored = tuple(module for module in modules if module.source_slots.get("def"))
        diagnostics = tuple(diagnostic for diagnostic in super().check(ctx, authored, collections) if diagnostic.code != "decision.missing_collection")
        return (
            *diagnostics,
            *(diagnostic for module in authored if (diagnostic := _category_shape_diagnostic(module)) is not None),
        )

    def emit(
        self,
        ctx: BuildContext,
        modules: tuple[Module, ...],
        collections: tuple[Collection, ...],
    ) -> tuple[Artifact, ...]:
        """Emit authored decisions and source-path-preserving shared files."""

        shared = tuple(module for module in modules if module.source_slots.get("shared_pdx"))
        owned = tuple(module for module in modules if not module.source_slots.get("shared_pdx"))
        shared_family = SimpleSourceFamily(
            family=self.family,
            pdx_path_template="{source_path}",
            source_slots=self.source_slots,
        )
        return (
            *super().emit(ctx, owned, collections),
            *shared_family.emit(ctx, shared, ()),
        )


def build_family() -> PIHC3DecisionFamily:
    """HeavenBase Registry target for the PIHC3 decision compiler."""

    return PIHC3DecisionFamily()


def _with_inferred_collection(module: Module) -> Module:
    if module.collection_id:
        return module
    category_ids = _decision_category_ids(module)
    if len(category_ids) != 1:
        return module
    return replace(module, collection_id=category_ids[0])


def _category_shape_diagnostic(module: Module) -> Diagnostic | None:
    category_ids = _decision_category_ids(module)
    if len(category_ids) == 1:
        return None
    if not category_ids:
        message = f"Decision module {module.module_id} must declare exactly one " "decision-category block in def.txt."
        code = "decision.missing_category"
    else:
        message = (
            f"Decision module {module.module_id} declares multiple decision " f"categories ({', '.join(category_ids)}); split them into standalone modules."
        )
        code = "decision.ambiguous_category"
    return Diagnostic(
        code=code,
        message=message,
        severity="error",
        module_id=module.module_id,
        source_path=_decision_definition_path(module),
    )


def _decision_category_ids(module: Module) -> tuple[str, ...]:
    category_ids: list[str] = []
    for source in getattr(module.payload, "pdx_sources", ()):
        if source.slot != "def":
            continue
        for entry in source.block.entries:
            if entry.key_str and isinstance(entry.val, PDXBlock) and entry.key_str not in category_ids:
                category_ids.append(entry.key_str)
    return tuple(category_ids)


def _decision_definition_path(module: Module) -> str:
    for source in getattr(module.payload, "pdx_sources", ()):
        if source.slot == "def":
            return source.path
    return "def.txt"
