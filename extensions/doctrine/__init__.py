"""PIHC3 doctrine Entity and routed compiler."""

from __future__ import annotations

import math
import re
from collections.abc import Mapping, Sequence
from dataclasses import replace

import heavenbase as hb

from paradev.build import (
    Artifact,
    BuildContext,
    Collection,
    Diagnostic,
    FamilyNormalizeResult,
    Module,
    ModuleDiagramContext,
    ModuleDiagramModuleCreation,
    ModuleDiagramNodeAuthoring,
    ModuleDiagramNodeField,
    ModuleDiagramProvider,
    ModuleDiagramSelectionDefault,
    ModuleSourceBundle,
    RoutedSourceFamily,
    SimpleSourceFamily,
    Slot,
    SourceRoute,
)
from paradev.games.hoi4.diagram_providers import (
    DOCTRINE_DIAGRAM_PROVIDER,
)
from paradev.games.hoi4.doctrine import (
    doctrine_diagram_projection,
    plan_doctrine_diagram_edits,
)
from paradev.pdx import PDXBlock, PDXScalar

_DOCTRINE_IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_.-]*\Z")
_SOURCE_FORM_FIELD_HINTS = {
    "folder": {
        "label": {"default": "Doctrine folder", "zh": "教义分类"},
        "description": {
            "default": "Top-level doctrine folder that contains this grand doctrine.",
            "zh": "包含此主教义的顶层教义分类。",
        },
    },
    "name": {
        "label": {"default": "Display name key", "zh": "显示名称键"},
        "description": {
            "default": "Localization key used as the doctrine's displayed name.",
            "zh": "作为此教义显示名称的本地化键。",
        },
    },
    "description": {
        "label": {"default": "Description key", "zh": "描述文本键"},
        "description": {
            "default": "Localization key used for the doctrine description.",
            "zh": "用于此教义描述文本的本地化键。",
        },
    },
    "icon": {
        "label": {"default": "Icon sprite", "zh": "教义图标精灵"},
        "description": {
            "default": "GFX sprite identifier displayed for this doctrine node.",
            "zh": "此教义节点显示的 GFX 精灵标识。",
        },
    },
    "xp_cost": {
        "label": {"default": "Experience cost", "zh": "经验花费"},
        "description": {
            "default": "Experience points required to unlock this doctrine.",
            "zh": "解锁此教义所需的经验点数。",
        },
    },
    "xp_type": {
        "label": {"default": "Experience type", "zh": "经验类型"},
        "description": {
            "default": "Experience pool spent by this doctrine: army, air, or navy.",
            "zh": "此教义消耗的经验池：army、air 或 navy。",
        },
    },
    "track": {
        "label": {"default": "Doctrine track", "zh": "教义路线"},
        "description": {
            "default": "Track identifier containing this subdoctrine.",
            "zh": "包含此子教义的路线标识。",
        },
    },
    "available": {
        "label": {"default": "Availability conditions", "zh": "可用条件"},
        "description": {
            "default": "Conditions that must be satisfied before this doctrine can be selected.",
            "zh": "选择此教义前必须满足的条件。",
        },
        "control": "block-text",
    },
    "visible": {
        "label": {"default": "Visibility conditions", "zh": "显示条件"},
        "description": {
            "default": "Conditions controlling whether this doctrine is shown in the tree.",
            "zh": "控制此教义是否显示在教义树中的条件。",
        },
        "control": "block-text",
    },
    "ai_will_do": {
        "label": {"default": "AI selection weight", "zh": "AI 选择权重"},
        "description": {
            "default": "AI weighting rules for choosing this doctrine.",
            "zh": "AI 选择此教义时使用的权重规则。",
        },
        "control": "block-text",
    },
    "tracks": {
        "label": {"default": "Doctrine tracks", "zh": "教义路线列表"},
        "description": {
            "default": "Track identifiers advanced by this grand doctrine.",
            "zh": "此主教义所推进的路线标识列表。",
        },
        "control": "block-text",
    },
    "milestones": {
        "label": {"default": "Milestones", "zh": "教义里程碑"},
        "description": {
            "default": "Ordered milestone effects executed while progressing this doctrine.",
            "zh": "推进此教义时按顺序执行的里程碑效果。",
        },
        "control": "block-text",
    },
    "rewards": {
        "label": {"default": "Doctrine rewards", "zh": "教义奖励"},
        "description": {
            "default": "Reward identifiers granted by this doctrine node.",
            "zh": "此教义节点授予的奖励标识。",
        },
        "control": "block-text",
    },
    "modifier": {
        "label": {"default": "Doctrine modifiers", "zh": "教义修正"},
        "description": {
            "default": "Country or unit modifiers granted by this doctrine.",
            "zh": "此教义提供的国家或部队修正。",
        },
        "control": "block-text",
    },
    "equipment_bonus": {
        "label": {"default": "Equipment bonuses", "zh": "装备加成"},
        "description": {
            "default": "Equipment-stat bonuses granted by this doctrine reward.",
            "zh": "此教义奖励提供的装备属性加成。",
        },
        "control": "block-text",
    },
}


class PIHC3Doctrine(hb.Entity):
    """One independently editable PIHC3 doctrine node or shared source set."""

    identifier = "pihc3-doctrine"
    title = hb.field(hb.ShortText).default("")
    subtype = hb.field(hb.ShortText).default("")
    family = "doctrine"
    resource_slots = (
        Slot("def", "def.txt", kind="pdx"),
        Slot("loc", "**/*.loc", many=True, kind="loc"),
        Slot("preview", "icon.png"),
        Slot(
            "shared_pdx",
            r"^common/doctrines/.*\.txt$",
            many=True,
            regex=True,
            kind="pdx",
        ),
        Slot(
            "shared_loc",
            r"^localisation/.*\.yml$",
            many=True,
            regex=True,
            kind="copy",
            authoring_path="localisation/english/{filename}",
        ),
    )
    compilation_hooks = ("normalize", "check", "emit")
    source_form_field_hints = _SOURCE_FORM_FIELD_HINTS

    @classmethod
    def build_family(cls) -> PIHC3DoctrineFamily:
        """Return the subtype-routed doctrine compiler."""

        return PIHC3DoctrineFamily()


class PIHC3DoctrineFamily(RoutedSourceFamily):
    """Compile each doctrine subtype to its required HoI4 path."""

    replaces_registered_family = True
    source_form_field_hints = _SOURCE_FORM_FIELD_HINTS

    def __init__(self) -> None:
        loc = "localisation/{language_folder}/{object_id}_{language}.yml"
        super().__init__(
            family=PIHC3Doctrine.family,
            routes={
                "air_sub": SourceRoute(
                    pdx_path_template=(
                        "common/doctrines/subdoctrines/air/{object_id}.txt"
                    ),
                    loc_path_template=loc,
                ),
                "folder": SourceRoute(
                    pdx_path_template=("common/doctrines/folders/{object_id}.txt"),
                    loc_path_template=loc,
                ),
                "grand": SourceRoute(
                    pdx_path_template=(
                        "common/doctrines/grand_doctrines/{object_id}.txt"
                    ),
                    loc_path_template=loc,
                ),
                "land_sub": SourceRoute(
                    pdx_path_template=(
                        "common/doctrines/subdoctrines/land/{object_id}.txt"
                    ),
                    loc_path_template=loc,
                ),
                "sea_sub": SourceRoute(
                    pdx_path_template=(
                        "common/doctrines/subdoctrines/sea/{object_id}.txt"
                    ),
                    loc_path_template=loc,
                ),
                "track": SourceRoute(
                    pdx_path_template=("common/doctrines/tracks/{object_id}.txt"),
                    loc_path_template=loc,
                ),
            },
            settings_key="subtype",
            source_slots=PIHC3Doctrine.resource_slots,
            required_loc_keys=("{object_id}", "{object_id}_desc"),
        )

    def normalize(
        self,
        ctx: BuildContext,
        modules: tuple[Module, ...],
        collections: tuple[Collection, ...],
    ) -> FamilyNormalizeResult:
        """Infer ordinary grand, land, air, and sea routes from doctrine PDX."""

        authored, support = _partition_modules(modules)
        inferred = tuple(_module_with_inferred_subtype(module) for module in authored)
        normalized = super().normalize(ctx, inferred, collections)
        return FamilyNormalizeResult(
            modules=(*normalized.modules, *support),
            diagnostics=normalized.diagnostics,
        )

    def check(
        self,
        ctx: BuildContext,
        modules: tuple[Module, ...],
        collections: tuple[Collection, ...],
    ) -> tuple[Diagnostic, ...]:
        """Validate doctrine nodes without imposing node fields on shared support."""

        authored, _support = _partition_modules(modules)
        diagnostics = list(super().check(ctx, authored, collections))
        for module in modules:
            has_definition = bool(module.source_slots.get("def"))
            has_support = bool(module.source_slots.get("shared_pdx"))
            if has_definition == has_support:
                diagnostics.append(
                    Diagnostic(
                        code="pihc3.doctrine.invalid_source_ownership",
                        message=(
                            f"Module {module.module_id} must own either one doctrine "
                            "definition or shared doctrine sources, but not both."
                        ),
                        severity="error",
                        module_id=module.module_id,
                    )
                )
        return tuple(diagnostics)

    def emit(
        self,
        ctx: BuildContext,
        modules: tuple[Module, ...],
        collections: tuple[Collection, ...],
    ) -> tuple[Artifact, ...]:
        """Emit routed doctrine nodes and path-preserving shared support files."""

        authored, support = _partition_modules(modules)
        support_family = SimpleSourceFamily(
            family=self.family,
            pdx_path_template="{source_path}",
            copy_path_template="{source_path}",
            source_slots=self.source_slots,
        )
        return (
            *super().emit(ctx, authored, collections),
            *support_family.emit(ctx, support, ()),
        )


def build_family() -> PIHC3DoctrineFamily:
    """HeavenBase Registry target for the doctrine compiler."""

    return PIHC3Doctrine.build_family()


def diagram_provider() -> ModuleDiagramProvider:
    """Return the PIHC3-owned doctrine-tree authoring provider."""

    return replace(
        DOCTRINE_DIAGRAM_PROVIDER,
        replaces_registered_provider=True,
        project=_project_doctrine,
        plan=_plan_doctrine,
        node_plan=_doctrine_node_plan,
        node_authoring=_DOCTRINE_NODE_AUTHORING,
        authoring_kind="diagram-node",
        selection_defaults=(),
    )


def _partition_modules(
    modules: tuple[Module, ...],
) -> tuple[tuple[Module, ...], tuple[Module, ...]]:
    authored = tuple(module for module in modules if module.source_slots.get("def"))
    support = tuple(module for module in modules if not module.source_slots.get("def"))
    return authored, support


def _doctrine_sources(
    context: ModuleDiagramContext,
) -> tuple[
    tuple[dict[str, object], ...],
    dict[str, ModuleSourceBundle],
    tuple[str, ...],
]:
    rows: list[dict[str, object]] = []
    owners: dict[str, ModuleSourceBundle] = {}
    support_modules: list[str] = []
    for module in sorted(
        context.modules,
        key=lambda row: (str(row.module_id or ""), str(row.root)),
    ):
        module_id = module.module_id
        if not isinstance(module_id, str) or not module_id:
            raise ValueError(
                "Every PIHC3 doctrine source bundle must have a canonical module id."
            )
        family, separator, object_id = module_id.partition("/")
        if separator != "/" or family != context.family or not object_id:
            raise ValueError(
                f"PIHC3 doctrine diagram received invalid module {module_id!r}."
            )
        definitions = tuple(module.source_slots.get("def", ()))
        shared_sources = tuple(module.source_slots.get("shared_pdx", ()))
        if not definitions:
            if not shared_sources:
                raise ValueError(
                    f"PIHC3 doctrine module {module_id!r} has neither an authored "
                    "definition nor shared PDX sources."
                )
            support_modules.append(module_id)
            continue
        if len(definitions) != 1 or shared_sources:
            raise ValueError(
                f"PIHC3 doctrine module {module_id!r} must own exactly one canonical "
                "'def' source and no shared PDX sources."
            )
        definition = context.read_module_text(module, definitions[0])
        if definition.path in owners:
            raise ValueError(
                f"PIHC3 doctrine source {definition.path!r} has more than one module owner."
            )
        owners[definition.path] = module
        diagram_path = ".paradev/diagram.yaml"
        diagram = context.read_optional_module_text(module, diagram_path)
        rows.append(
            {
                "object_id": object_id,
                "module_id": module_id,
                "definition_path": definition.path,
                "definition_text": definition.text,
                "diagram_path": (
                    diagram.path
                    if diagram is not None
                    else context.module_source_path(module, diagram_path)
                ),
                "diagram_text": diagram.text if diagram is not None else None,
            }
        )
    return tuple(rows), owners, tuple(sorted(support_modules))


def _localized_values(
    module: ModuleSourceBundle,
    key: str,
) -> dict[str, str]:
    values: dict[str, str] = {}
    for entry in sorted(
        module.loc_entries,
        key=lambda row: (row.language, row.source_path, row.text),
    ):
        if entry.key == key and entry.text.strip():
            values.setdefault(entry.language, entry.text.strip())
    return dict(sorted(values.items()))


def _authored_definition(module: ModuleSourceBundle) -> PDXBlock:
    sources = tuple(source for source in module.pdx_sources if source.slot == "def")
    if len(sources) != 1:
        raise ValueError(
            f"PIHC3 doctrine module {module.module_id!r} must own exactly one parsed definition."
        )
    entries = [
        entry
        for entry in sources[0].block.entries
        if entry.key_str and isinstance(entry.val, PDXBlock)
    ]
    if len(entries) != 1:
        raise ValueError(
            f"PIHC3 doctrine module {module.module_id!r} must contain one doctrine block."
        )
    return entries[0].val


def _project_doctrine(
    context: ModuleDiagramContext,
) -> Mapping[str, object]:
    sources, owners, support_modules = _doctrine_sources(context)
    projection = dict(doctrine_diagram_projection(sources))
    nodes: list[object] = []
    for value in projection.get("nodes", []):
        if not isinstance(value, Mapping):
            nodes.append(value)
            continue
        row = dict(value)
        source_path = row.get("source_path")
        module = owners.get(source_path) if isinstance(source_path, str) else None
        if module is None or not isinstance(module.module_id, str):
            raise ValueError(
                f"PIHC3 doctrine projection source {source_path!r} has no reviewed module owner."
            )
        block = _authored_definition(module)
        name_key = _block_scalar(block, "name") or str(row["id"])
        description_key = _block_scalar(block, "description") or f"{name_key}_desc"
        row["module_id"] = module.module_id
        row["name_key"] = name_key
        row["description_key"] = description_key
        for field in ("folder", "track", "xp_type", "icon"):
            field_value = _block_scalar(block, field)
            if field_value is not None:
                row[field] = field_value
        titles = _localized_values(module, name_key)
        descriptions = _localized_values(module, description_key)
        if titles:
            row["localized_titles"] = titles
        if descriptions:
            row["localized_descriptions"] = descriptions
        previews = tuple(module.source_slots.get("preview", ()))
        if len(previews) > 1:
            raise ValueError(
                f"PIHC3 doctrine module {module.module_id!r} owns more than one preview image."
            )
        if previews:
            row["image_path"] = context.module_source_path(module, previews[0])
        nodes.append(row)
    projection["source_kind"] = "pihc3_doctrine_modules"
    projection["nodes"] = nodes
    projection["module_ids"] = sorted(
        module.module_id
        for module in context.modules
        if isinstance(module.module_id, str)
    )
    projection["support_module_ids"] = list(support_modules)
    summary = projection.get("summary")
    if isinstance(summary, Mapping):
        projection["summary"] = {
            **summary,
            "module_count": len(context.modules),
            "support_module_count": len(support_modules),
        }
    return projection


def _plan_doctrine(
    context: ModuleDiagramContext,
    position_intents: Sequence[Mapping[str, object]],
    edge_intents: Sequence[Mapping[str, object]],
) -> Mapping[str, object]:
    sources, _owners, _support_modules = _doctrine_sources(context)
    return plan_doctrine_diagram_edits(
        sources,
        position_intents=position_intents,
        edge_intents=edge_intents,
    )


def _required_text(intent: Mapping[str, object], field: str) -> str:
    value = intent.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"PIHC3 doctrine creation requires a non-empty {field}.")
    return value.strip()


def _required_identifier(intent: Mapping[str, object], field: str) -> str:
    value = _required_text(intent, field)
    if _DOCTRINE_IDENTIFIER.fullmatch(value) is None:
        raise ValueError(
            f"PIHC3 doctrine creation {field} must be a path-safe game identifier."
        )
    return value


def _identifier_or_default(
    intent: Mapping[str, object],
    field: str,
    *,
    default: str,
) -> str:
    value = intent.get(field, default)
    if (
        not isinstance(value, str)
        or _DOCTRINE_IDENTIFIER.fullmatch(value.strip()) is None
    ):
        raise ValueError(
            f"PIHC3 doctrine creation {field} must be a path-safe game identifier."
        )
    return value.strip()


def _optional_identifier(
    intent: Mapping[str, object],
    field: str,
) -> str | None:
    value = intent.get(field)
    if value is None or value == "":
        return None
    if (
        not isinstance(value, str)
        or _DOCTRINE_IDENTIFIER.fullmatch(value.strip()) is None
    ):
        raise ValueError(
            f"PIHC3 doctrine creation {field} must be a path-safe game identifier."
        )
    return value.strip()


def _bounded_integer(
    intent: Mapping[str, object],
    field: str,
    *,
    default: int,
) -> int:
    value = intent.get(field, default)
    if type(value) is not int or abs(value) > 100_000:
        raise ValueError(
            f"PIHC3 doctrine creation {field} must be an integer between -100000 and 100000."
        )
    return value


def _finite_number(
    intent: Mapping[str, object],
    field: str,
    *,
    default: float,
    positive: bool = False,
) -> int | float:
    value = intent.get(field, default)
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        or abs(value) > 10_000
        or (positive and value <= 0)
    ):
        requirement = (
            "greater than 0 and at most 10000"
            if positive
            else "between -10000 and 10000"
        )
        raise ValueError(
            f"PIHC3 doctrine creation {field} must be a finite number {requirement}."
        )
    return value


def _doctrine_node_plan(
    context: ModuleDiagramContext,
    intent: Mapping[str, object],
) -> ModuleDiagramModuleCreation:
    """Resolve one tree intent into a standalone PIHC3 Doctrine Entity."""

    doctrine_id = _required_identifier(intent, "doctrine_id")
    title = _required_text(intent, "title")
    if "\n" in title or "\r" in title:
        raise ValueError("PIHC3 doctrine title must fit on one line.")
    description_value = intent.get("description", "")
    if not isinstance(description_value, str):
        raise TypeError("PIHC3 doctrine creation description must be text.")
    description = description_value.strip()
    track = _identifier_or_default(intent, "track", default="infantry")
    xp_type = _identifier_or_default(intent, "xp_type", default="army")
    if xp_type not in {"air", "army", "navy"}:
        raise ValueError("PIHC3 doctrine creation xp_type must be air, army, or navy.")
    icon = _identifier_or_default(
        intent,
        "icon",
        default="GFX_doctrine_mobile_warfare_medium",
    )
    modifier = _identifier_or_default(
        intent,
        "modifier",
        default="planning_speed",
    )
    xp_cost = _finite_number(
        intent,
        "xp_cost",
        default=100,
        positive=True,
    )
    ai_factor = _finite_number(
        intent,
        "ai_factor",
        default=1,
        positive=True,
    )
    modifier_value = _finite_number(intent, "modifier_value", default=0.05)
    x = _bounded_integer(intent, "x", default=0)
    y = _bounded_integer(intent, "y", default=0)
    parent_doctrine_id = _optional_identifier(intent, "parent_doctrine_id")

    projection = _project_doctrine(context)
    nodes = {
        str(row["id"]): row
        for row in projection.get("nodes", [])
        if isinstance(row, Mapping) and isinstance(row.get("id"), str)
    }
    if doctrine_id in nodes or any(
        row.get("compiled_id") == doctrine_id for row in nodes.values()
    ):
        raise ValueError(f"PIHC3 doctrine {doctrine_id!r} already exists.")
    parent = nodes.get(parent_doctrine_id) if parent_doctrine_id is not None else None
    if parent_doctrine_id is not None and parent is None:
        raise ValueError(
            f"PIHC3 doctrine parent_doctrine_id {parent_doctrine_id!r} must "
            "identify an existing doctrine."
        )
    definition_sources = [
        {
            "doctrine_id": str(row["id"]),
            "compiled_id": row.get("compiled_id"),
            "source_path": row.get("source_path"),
            "definition_source_revision": row.get("definition_source_revision"),
        }
        for row in sorted(nodes.values(), key=lambda value: str(value["id"]))
    ]
    source_plan: Mapping[str, object] | None = None
    if parent_doctrine_id is not None and isinstance(parent, Mapping):
        sources, _owners, _support_modules = _doctrine_sources(context)
        source_plan = plan_doctrine_diagram_edits(
            sources,
            edge_intents=(
                {
                    "kind": "path",
                    "source_id": parent_doctrine_id,
                    "target_id": doctrine_id,
                    "present": True,
                    "source_revision": parent.get("source_revision"),
                },
            ),
            pending_node_ids=(doctrine_id,),
        )
    return ModuleDiagramModuleCreation(
        schema="paradev.pihc3.doctrine-node-module-create.v1",
        family_or_template="pihc3:doctrine/subdoctrine-basic",
        object_id=doctrine_id,
        values={
            "title": title,
            "description": description,
            "track": track,
            "xp_type": xp_type,
            "icon": icon,
            "xp_cost": xp_cost,
            "ai_factor": ai_factor,
            "modifier": modifier,
            "modifier_value": modifier_value,
            "language": context.preferred_language,
            "diagram_x": x,
            "diagram_y": y,
            "diagram_paths": "[]",
        },
        intent={
            "doctrine_id": doctrine_id,
            "title": title,
            "description": description,
            "track": track,
            "xp_type": xp_type,
            "icon": icon,
            "xp_cost": xp_cost,
            "ai_factor": ai_factor,
            "modifier": modifier,
            "modifier_value": modifier_value,
            "x": x,
            "y": y,
            "parent_doctrine_id": parent_doctrine_id,
            "parent_source_revision": (
                parent.get("source_revision") if isinstance(parent, Mapping) else None
            ),
            "parent_definition_source_revision": (
                parent.get("definition_source_revision")
                if isinstance(parent, Mapping)
                else None
            ),
            "definition_sources": definition_sources,
            "language": context.preferred_language,
        },
        source_plan=source_plan,
    )


_DOCTRINE_NODE_AUTHORING = ModuleDiagramNodeAuthoring(
    title="Add PIHC3 doctrine",
    description=(
        "Create one independently editable subdoctrine module. Selecting a doctrine "
        "prefills it as the parent that unlocks the new child; clear Parent doctrine "
        "to create an unconnected root."
    ),
    fields=(
        ModuleDiagramNodeField(
            name="doctrine_id",
            label="Doctrine ID",
            required=True,
            description="Stable game identifier, for example DOCTRINE_NEW_LOGISTICS.",
        ),
        ModuleDiagramNodeField(name="title", label="Name", required=True),
        ModuleDiagramNodeField(
            name="description",
            label="Description",
            kind="textarea",
        ),
        ModuleDiagramNodeField(
            name="track",
            label="Doctrine track",
            default="infantry",
        ),
        ModuleDiagramNodeField(
            name="xp_type",
            label="Experience type",
            default="army",
            description="Use army, air, or navy.",
        ),
        ModuleDiagramNodeField(name="x", label="X position", kind="number", default=0),
        ModuleDiagramNodeField(name="y", label="Y position", kind="number", default=0),
        ModuleDiagramNodeField(
            name="parent_doctrine_id",
            label="Parent doctrine",
            description="Existing doctrine that unlocks this new child.",
            advanced=True,
        ),
        ModuleDiagramNodeField(
            name="icon",
            label="Icon sprite",
            default="GFX_doctrine_mobile_warfare_medium",
            advanced=True,
        ),
        ModuleDiagramNodeField(
            name="xp_cost",
            label="Experience cost",
            kind="number",
            default=100,
            advanced=True,
        ),
        ModuleDiagramNodeField(
            name="ai_factor",
            label="AI weight",
            kind="number",
            default=1,
            advanced=True,
        ),
        ModuleDiagramNodeField(
            name="modifier",
            label="Modifier",
            default="planning_speed",
            advanced=True,
        ),
        ModuleDiagramNodeField(
            name="modifier_value",
            label="Modifier value",
            kind="number",
            default=0.05,
            description="Decimal modifier; use 0.05 for 5%.",
            advanced=True,
        ),
    ),
    selection_defaults=(
        ModuleDiagramSelectionDefault(field="parent_doctrine_id", source="id"),
        ModuleDiagramSelectionDefault(field="xp_type", source="xp_type"),
        ModuleDiagramSelectionDefault(field="x", source="x"),
        ModuleDiagramSelectionDefault(field="y", source="y", offset=2),
    ),
    requires_selection=False,
)


def _module_with_inferred_subtype(module: Module) -> Module:
    settings = module.metadata.get("settings")
    if isinstance(settings, dict) and settings.get("subtype"):
        return module
    subtype = _inferred_subtype(module)
    if subtype is None:
        return module
    metadata = dict(module.metadata)
    normalized_settings = dict(settings) if isinstance(settings, dict) else {}
    normalized_settings["subtype"] = subtype
    metadata["settings"] = normalized_settings
    payload = module.payload
    if isinstance(payload, ModuleSourceBundle):
        payload = replace(payload, metadata=dict(metadata))
    return replace(module, metadata=metadata, payload=payload)


def _inferred_subtype(module: Module) -> str | None:
    if not isinstance(module.payload, ModuleSourceBundle):
        return None
    for source in module.payload.pdx_sources:
        if source.slot != "def":
            continue
        for entry in source.block.entries:
            if not isinstance(entry.val, PDXBlock):
                continue
            if _block_scalar(entry.val, "folder"):
                return "grand"
            if not _block_scalar(entry.val, "track"):
                continue
            xp_type = (_block_scalar(entry.val, "xp_type") or "").casefold()
            return {
                "air": "air_sub",
                "army": "land_sub",
                "navy": "sea_sub",
            }.get(xp_type)
    return None


def _block_scalar(block: PDXBlock, key: str) -> str | None:
    for entry in block.entries:
        if entry.key_str == key and isinstance(entry.val, PDXScalar):
            return str(entry.val.val)
    return None
