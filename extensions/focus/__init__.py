"""PIHC3 compiler overlay for the built-in focus family."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import replace
from typing import ClassVar

from paradev.build import (
    BuildContext,
    Collection,
    CollectionPDXFamily,
    Diagnostic,
    ModuleDiagramContext,
    ModuleDiagramModuleCreation,
    ModuleDiagramNodeAuthoring,
    ModuleDiagramNodeField,
    ModuleDiagramProvider,
    ModuleDiagramSelectionDefault,
    Module,
    Slot,
)
from paradev.games.hoi4.diagram_providers import (
    FOCUS_TREE_DIAGRAM_PROVIDER,
)

_FOCUS_IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_.-]*\Z")
FOCUS_RESOURCE_SLOTS = (
    Slot("def", "def.txt", required=True, kind="pdx"),
    Slot("loc", "**/*.loc", many=True, kind="loc"),
    Slot("preview", "preview.png"),
    Slot(
        "compiled_assets",
        r"^gfx/interface/goals/.*\.dds$",
        many=True,
        regex=True,
        kind="copy",
        authoring_path="gfx/interface/goals/{filename}",
    ),
    Slot(
        "compiled_assets",
        r"^interface/focuses/.*\.gfx$",
        many=True,
        regex=True,
        kind="copy",
        authoring_path="interface/focuses/{filename}",
    ),
)
FOCUS_COLLECTION_RESOURCE_SLOTS = (
    Slot("def", "def.txt", required=True, kind="pdx"),
    Slot("loc", "**/*.loc", many=True, kind="loc"),
    Slot(
        "compiled_assets",
        r"^gfx/interface/goals/.*\.dds$",
        many=True,
        regex=True,
        kind="copy",
        authoring_path="gfx/interface/goals/{filename}",
    ),
    Slot(
        "compiled_assets",
        r"^interface/focuses/.*\.gfx$",
        many=True,
        regex=True,
        kind="copy",
        authoring_path="interface/focuses/{filename}",
    ),
)
FOCUS_SOURCE_FORM_FIELD_HINTS = {
    "icon": {
        "description": {
            "default": "Focus-icon sprite identifier displayed in the focus tree.",
            "zh": "国策树中显示的国策图标精灵标识。",
        }
    },
    "cost": {
        "description": {
            "default": "Focus completion cost in seven-day units.",
            "zh": "国策完成成本，以 7 天为一个单位。",
        }
    },
    "x": {
        "description": {
            "default": "Horizontal focus-tree grid position.",
            "zh": "国策树网格中的水平位置。",
        }
    },
    "y": {
        "description": {
            "default": "Vertical focus-tree grid position.",
            "zh": "国策树网格中的垂直位置。",
        }
    },
    "relative_position_id": {
        "description": {
            "default": "Focus identifier used as the relative positioning anchor.",
            "zh": "用作相对定位锚点的国策标识。",
        }
    },
}


class PIHC3FocusFamily(CollectionPDXFamily):
    """Compile ordered focus modules inside one focus-tree collection wrapper."""

    replaces_registered_family = True
    source_form_field_hints: ClassVar[dict[str, dict[str, object]]] = FOCUS_SOURCE_FORM_FIELD_HINTS

    def __init__(self) -> None:
        super().__init__(
            family="focus",
            pdx_path_template="common/national_focus/{collection_id}.txt",
            loc_path_template=("localisation/{language_folder}/" "FOCUS_TREE_{collection_id}_{language}.yml"),
            copy_path_template="{source_path}",
            source_slots=FOCUS_RESOURCE_SLOTS,
            collection_source_slots=FOCUS_COLLECTION_RESOURCE_SLOTS,
            member_container="focus_tree",
            aggregate_member_localization=True,
        )

    def check(
        self,
        ctx: BuildContext,
        modules: tuple[Module, ...],
        collections: tuple[Collection, ...],
    ) -> tuple[Diagnostic, ...]:
        """Keep migrated source parity while retaining graph diagnostics."""

        return tuple(diagnostic for diagnostic in super().check(ctx, modules, collections) if diagnostic.code != "focus.missing_localization")


def build_family() -> PIHC3FocusFamily:
    """HeavenBase Registry target for the PIHC3 focus compiler."""

    return PIHC3FocusFamily()


def _required_text(intent: Mapping[str, object], field: str) -> str:
    value = intent.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"PIHC3 focus creation requires a non-empty {field}.")
    return value.strip()


def _optional_identifier(intent: Mapping[str, object], field: str) -> str | None:
    value = intent.get(field)
    if value is None or value == "":
        return None
    if not isinstance(value, str) or _FOCUS_IDENTIFIER.fullmatch(value.strip()) is None:
        raise ValueError(f"PIHC3 focus creation {field} must be a path-safe game identifier.")
    return value.strip()


def _focus_node_plan(
    context: ModuleDiagramContext,
    intent: Mapping[str, object],
) -> ModuleDiagramModuleCreation:
    """Resolve one diagram intent into the PIHC3 focus template."""

    tree_id = _required_text(intent, "tree_id")
    focus_id = _required_text(intent, "focus_id")
    if _FOCUS_IDENTIFIER.fullmatch(tree_id) is None or _FOCUS_IDENTIFIER.fullmatch(focus_id) is None:
        raise ValueError("PIHC3 focus tree and focus IDs must be path-safe game identifiers.")
    title = _required_text(intent, "title")
    description = _required_text(intent, "description")
    if "\n" in title or "\r" in title:
        raise ValueError("PIHC3 focus title must fit on one line.")
    x = intent.get("x", 0)
    y = intent.get("y", 0)
    if any(type(value) is not int or abs(value) > 100_000 for value in (x, y)):
        raise ValueError("PIHC3 focus x and y must be integers between -100000 and 100000.")
    relative_position_id = _optional_identifier(intent, "relative_position_id")
    prerequisite_id = _optional_identifier(intent, "prerequisite_id")
    icon_key = _optional_identifier(intent, "icon_key") or "GFX_goal_generic_construct_civ_factory"

    projection = FOCUS_TREE_DIAGRAM_PROVIDER.project(context)
    trees = [row for row in projection.get("trees", []) if isinstance(row, Mapping) and row.get("id") == tree_id]
    if len(trees) != 1:
        raise ValueError(f"PIHC3 focus tree {tree_id!r} must resolve to exactly one editable collection.")
    tree = trees[0]
    collection_id = tree.get("collection_id")
    if not isinstance(collection_id, str) or not collection_id:
        raise ValueError(f"PIHC3 focus tree {tree_id!r} has no editable collection owner.")
    nodes = {str(row["id"]): row for row in projection.get("nodes", []) if isinstance(row, Mapping) and isinstance(row.get("id"), str)}
    if focus_id in nodes:
        raise ValueError(f"PIHC3 focus {focus_id!r} already exists.")
    for field, reference in (
        ("relative_position_id", relative_position_id),
        ("prerequisite_id", prerequisite_id),
    ):
        if reference is None:
            continue
        node = nodes.get(reference)
        if node is None or node.get("tree_id") != tree_id:
            raise ValueError(f"PIHC3 focus {field} {reference!r} must identify a focus in tree {tree_id!r}.")

    values = {
        "title": title,
        "description": description,
        "tree": collection_id,
        "icon": icon_key,
        "cost": 10,
        "x": x,
        "y": y,
        "relative_position": (f"relative_position_id = {relative_position_id}" if relative_position_id is not None else ""),
        "prerequisite": (f"prerequisite = {{ focus = {prerequisite_id} }}" if prerequisite_id is not None else ""),
        "language": context.preferred_language,
    }
    return ModuleDiagramModuleCreation(
        schema="paradev.pihc3.focus-node-module-create.v1",
        family_or_template="focus",
        object_id=focus_id,
        values=values,
        intent={
            "tree_id": tree_id,
            "collection_id": collection_id,
            "tree_source_revision": tree.get("source_revision"),
            "focus_id": focus_id,
            "x": x,
            "y": y,
            "title": title,
            "description": description,
            "relative_position_id": relative_position_id,
            "prerequisite_id": prerequisite_id,
            "icon_key": icon_key,
            "language": context.preferred_language,
        },
    )


_FOCUS_NODE_AUTHORING = ModuleDiagramNodeAuthoring(
    title="Add PIHC3 focus",
    description=("Create one independently editable Focus module in an existing tree. " "Selecting a focus prefills its tree and parent relationships."),
    fields=(
        ModuleDiagramNodeField(
            name="tree_id",
            label="Focus tree ID",
            required=True,
            description="Existing PIHC3 focus-tree identifier.",
        ),
        ModuleDiagramNodeField(
            name="focus_id",
            label="Focus ID",
            required=True,
            description="Stable game identifier, for example C08_NEW_DIRECTION.",
        ),
        ModuleDiagramNodeField(name="title", label="Name", required=True),
        ModuleDiagramNodeField(
            name="description",
            label="Description",
            kind="textarea",
            required=True,
        ),
        ModuleDiagramNodeField(name="x", label="X position", kind="number", default=0),
        ModuleDiagramNodeField(name="y", label="Y position", kind="number", default=0),
        ModuleDiagramNodeField(
            name="relative_position_id",
            label="Position parent",
            advanced=True,
        ),
        ModuleDiagramNodeField(
            name="prerequisite_id",
            label="Prerequisite",
            advanced=True,
        ),
        ModuleDiagramNodeField(
            name="icon_key",
            label="Icon sprite",
            default="GFX_goal_generic_construct_civ_factory",
            advanced=True,
        ),
    ),
    selection_defaults=(
        ModuleDiagramSelectionDefault(field="tree_id", source="tree_id"),
        ModuleDiagramSelectionDefault(field="relative_position_id", source="id"),
        ModuleDiagramSelectionDefault(field="prerequisite_id", source="id"),
        ModuleDiagramSelectionDefault(field="x", source="x"),
        ModuleDiagramSelectionDefault(field="y", source="y", offset=1),
    ),
    requires_selection=False,
)


def diagram_provider() -> ModuleDiagramProvider:
    """Return the PIHC3-owned focus-tree authoring provider."""

    return replace(
        FOCUS_TREE_DIAGRAM_PROVIDER,
        node_plan=_focus_node_plan,
        node_authoring=_FOCUS_NODE_AUTHORING,
        authoring_kind="diagram-node",
        replaces_registered_provider=True,
    )
