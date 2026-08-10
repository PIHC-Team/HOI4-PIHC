"""PIHC3 compiler overlay for the built-in idea family."""

from __future__ import annotations

from typing import ClassVar

from paradev.build import (
    Artifact,
    BuildContext,
    Collection,
    Diagnostic,
    Module,
    SimpleSourceFamily,
    Slot,
)
from paradev.games.hoi4 import IdeaFamily

IDEA_RESOURCE_SLOTS = (
    Slot("def", "def.txt", kind="pdx"),
    Slot("loc", "**/*.loc", many=True, kind="loc"),
    Slot("preview", "preview.png"),
    Slot(
        "compiled_assets",
        r"^gfx/interface/ideas/.*\.dds$",
        many=True,
        regex=True,
        kind="copy",
        authoring_path="gfx/interface/ideas/{filename}",
    ),
    Slot(
        "compiled_assets",
        r"^interface/ideas/.*\.gfx$",
        many=True,
        regex=True,
        kind="copy",
        authoring_path="interface/ideas/{filename}",
    ),
    Slot(
        "shared_pdx",
        r"^common/ideas/.*\.txt$",
        many=True,
        regex=True,
        kind="pdx",
    ),
)

IDEA_SOURCE_FORM_FIELD_HINTS = {
    "picture": {
        "description": {
            "default": "Sprite name used for this idea's icon.",
            "zh": "该理念图标使用的精灵名称。",
        }
    },
    "removal_cost": {
        "description": {
            "default": "Political-power cost to remove this idea; -1 makes it non-removable.",
            "zh": "移除该理念的政治点数代价；-1 表示不可移除。",
        }
    },
    "industrial_capacity_factory": {
        "description": {
            "default": "Civilian-factory output modifier as a decimal; 0.02 means 2%.",
            "zh": "民用工厂产出修正的小数值；0.02 表示 2%。",
        }
    },
}


class PIHC3IdeaFamily(IdeaFamily):
    """Add PIHC3 asset and shared-source behavior to built-in ideas."""

    replaces_registered_family = True
    source_form_field_hints: ClassVar[dict[str, dict[str, object]]] = IDEA_SOURCE_FORM_FIELD_HINTS

    def __init__(self) -> None:
        super().__init__(
            family="idea",
            pdx_path_template="common/ideas/{object_id}.txt",
            loc_path_template=("localisation/{language_folder}/{object_id}_{language}.yml"),
            copy_path_template="{source_path}",
            source_slots=IDEA_RESOURCE_SLOTS,
            required_loc_keys=("{object_id}", "{object_id}_desc"),
        )

    def check(
        self,
        ctx: BuildContext,
        modules: tuple[Module, ...],
        collections: tuple[Collection, ...],
    ) -> tuple[Diagnostic, ...]:
        """Validate authored idea nodes without imposing node fields on shared files."""

        authored = tuple(module for module in modules if module.source_slots.get("def"))
        return super().check(ctx, authored, collections)

    def emit(
        self,
        ctx: BuildContext,
        modules: tuple[Module, ...],
        collections: tuple[Collection, ...],
    ) -> tuple[Artifact, ...]:
        """Emit authored ideas and source-path-preserving shared files."""

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


def build_family() -> PIHC3IdeaFamily:
    """Return the PIHC3 overlay for the built-in idea family."""

    return PIHC3IdeaFamily()
