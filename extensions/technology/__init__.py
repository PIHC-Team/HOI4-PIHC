"""PIHC3 technology Entity and compiler."""

from __future__ import annotations

import math
import re
from collections.abc import Mapping, Sequence
from dataclasses import replace
from typing import ClassVar

import heavenbase as hb

from paradev.build import (
    Artifact,
    BuildContext,
    Collection,
    Diagnostic,
    Module,
    ModuleDiagramContext,
    ModuleDiagramModuleCreation,
    ModuleDiagramNodeAuthoring,
    ModuleDiagramNodeField,
    ModuleDiagramProvider,
    ModuleDiagramSelectionDefault,
    ModuleSourceBundle,
    SimpleSourceFamily,
    Slot,
)
from paradev.games.hoi4.diagram_providers import (
    TECHNOLOGY_DIAGRAM_PROVIDER,
)
from paradev.games.hoi4.technology import (
    plan_technology_diagram_edits,
    technology_diagram_projection,
)

_TECHNOLOGY_IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_.-]*\Z")


class PIHC3Technology(hb.Entity):
    """One independently editable PIHC3 technology or shared source set."""

    identifier = "pihc3-technology"
    title = hb.field(hb.ShortText).default("")
    description = hb.field(hb.LongText).default("")
    family = "technology"
    resource_slots = (
        Slot("def", "def.txt", kind="pdx"),
        Slot("loc", "**/*.loc", many=True, kind="loc"),
        Slot("preview", "icon.png"),
        Slot(
            "compiled_assets",
            r"^gfx/interface/technologies/.*\.dds$",
            many=True,
            regex=True,
            kind="copy",
            authoring_path="gfx/interface/technologies/{filename}",
        ),
        Slot(
            "compiled_assets",
            r"^interface/technologies/.*\.gfx$",
            many=True,
            regex=True,
            kind="copy",
            authoring_path="interface/technologies/{filename}",
        ),
        Slot(
            "shared_pdx",
            r"^common/technologies/.*\.txt$",
            many=True,
            regex=True,
            kind="pdx",
        ),
    )
    compilation_hooks = ("normalize", "check", "emit")
    # HeavenBase Entity annotations are logical fields; protocol metadata stays unannotated.
    source_form_field_hints = {  # noqa: RUF012
        "research_cost": {
            "description": {
                "default": "Base research-time multiplier for this technology.",
                "zh": "该科技的基础研究时间倍率。",
            }
        },
        "start_year": {
            "description": {
                "default": "Historical year used for ahead-of-time research penalties.",
                "zh": "用于计算超前研究惩罚的历史年份。",
            }
        },
        "x": {
            "description": {
                "default": "Horizontal technology-tree grid position.",
                "zh": "科技树网格中的水平位置。",
            }
        },
        "y": {
            "description": {
                "default": "Vertical technology-tree grid position.",
                "zh": "科技树网格中的垂直位置。",
            }
        },
        "leads_to_tech": {
            "description": {
                "default": "Technology identifier reached by this tree connection.",
                "zh": "该科技树连线指向的科技标识。",
            }
        },
    }

    @classmethod
    def build_family(cls) -> PIHC3TechnologyFamily:
        """Return the technology compiler."""

        return PIHC3TechnologyFamily()


class PIHC3TechnologyFamily(SimpleSourceFamily):
    """Compile technology nodes, owned icons, and shared source files."""

    replaces_registered_family = True
    source_form_field_hints: ClassVar[dict[str, dict[str, object]]] = PIHC3Technology.source_form_field_hints

    def __init__(self) -> None:
        super().__init__(
            family=PIHC3Technology.family,
            pdx_path_template="common/technologies/{object_id}.txt",
            loc_path_template=("localisation/{language_folder}/{object_id}_{language}.yml"),
            copy_path_template="{source_path}",
            source_slots=PIHC3Technology.resource_slots,
            required_loc_keys=("{object_id}", "{object_id}_desc"),
        )

    def check(
        self,
        ctx: BuildContext,
        modules: tuple[Module, ...],
        collections: tuple[Collection, ...],
    ) -> tuple[Diagnostic, ...]:
        """Validate authored technology nodes without imposing node fields on support."""

        authored = tuple(module for module in modules if module.source_slots.get("def"))
        return super().check(ctx, authored, collections)

    def emit(
        self,
        ctx: BuildContext,
        modules: tuple[Module, ...],
        collections: tuple[Collection, ...],
    ) -> tuple[Artifact, ...]:
        """Emit authored technologies and source-path-preserving shared files."""

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


def build_family() -> PIHC3TechnologyFamily:
    """HeavenBase Registry target for the technology compiler."""

    return PIHC3Technology.build_family()


def _required_text(intent: Mapping[str, object], field: str) -> str:
    value = intent.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"PIHC3 technology creation requires a non-empty {field}.")
    return value.strip()


def _required_identifier(intent: Mapping[str, object], field: str) -> str:
    value = _required_text(intent, field)
    if _TECHNOLOGY_IDENTIFIER.fullmatch(value) is None:
        raise ValueError(f"PIHC3 technology creation {field} must be a path-safe game identifier.")
    return value


def _identifier_or_default(
    intent: Mapping[str, object],
    field: str,
    *,
    default: str,
) -> str:
    value = intent.get(field, default)
    if not isinstance(value, str) or _TECHNOLOGY_IDENTIFIER.fullmatch(value.strip()) is None:
        raise ValueError(f"PIHC3 technology creation {field} must be a path-safe game identifier.")
    return value.strip()


def _optional_identifier(intent: Mapping[str, object], field: str) -> str | None:
    value = intent.get(field)
    if value is None or value == "":
        return None
    if not isinstance(value, str) or _TECHNOLOGY_IDENTIFIER.fullmatch(value.strip()) is None:
        raise ValueError(f"PIHC3 technology creation {field} must be a path-safe game identifier.")
    return value.strip()


def _bounded_integer(
    intent: Mapping[str, object],
    field: str,
    *,
    default: int,
    minimum: int,
    maximum: int,
) -> int:
    value = intent.get(field, default)
    if type(value) is not int or value < minimum or value > maximum:
        raise ValueError(f"PIHC3 technology creation {field} must be an integer between {minimum} and {maximum}.")
    return value


def _positive_number(
    intent: Mapping[str, object],
    field: str,
    *,
    default: float,
) -> int | float:
    value = intent.get(field, default)
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0 or value > 10_000:
        raise ValueError(f"PIHC3 technology creation {field} must be a finite number greater than 0 and at most 10000.")
    return value


def _technology_sources(
    context: ModuleDiagramContext,
) -> tuple[
    tuple[dict[str, str], ...],
    dict[str, ModuleSourceBundle],
    tuple[str, ...],
]:
    """Read node definitions while retaining legitimate shared-source modules."""

    rows: list[dict[str, str]] = []
    owners: dict[str, ModuleSourceBundle] = {}
    support_modules: list[str] = []
    for module in sorted(
        context.modules,
        key=lambda row: (str(row.module_id or ""), str(row.root)),
    ):
        module_id = module.module_id
        if not isinstance(module_id, str) or not module_id:
            raise ValueError("Every PIHC3 technology source bundle must have a canonical module id.")
        definitions = tuple(module.source_slots.get("def", ()))
        shared_sources = tuple(module.source_slots.get("shared_pdx", ()))
        if not definitions:
            if not shared_sources:
                raise ValueError(f"PIHC3 technology module {module_id!r} has neither an authored definition nor a shared PDX source.")
            support_modules.append(module_id)
            continue
        if len(definitions) != 1:
            raise ValueError(f"PIHC3 technology module {module_id!r} must own exactly one canonical 'def' source; found {len(definitions)}.")
        definition = context.read_module_text(module, definitions[0])
        if definition.path in owners:
            raise ValueError(f"PIHC3 technology source {definition.path!r} has more than one module owner.")
        owners[definition.path] = module
        rows.append({"path": definition.path, "text": definition.text})
    rows.sort(key=lambda row: row["path"])
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


def _technology_projection(
    context: ModuleDiagramContext,
) -> Mapping[str, object]:
    sources, owners, support_modules = _technology_sources(context)
    projection = technology_diagram_projection(sources)
    nodes: list[object] = []
    for value in projection.get("nodes", []):
        if not isinstance(value, Mapping):
            nodes.append(value)
            continue
        row = dict(value)
        source_path = row.get("source_path")
        module = owners.get(source_path) if isinstance(source_path, str) else None
        if module is None or not isinstance(module.module_id, str):
            raise ValueError(f"PIHC3 technology projection source {source_path!r} has no reviewed module owner.")
        row["module_id"] = module.module_id
        technology_id = row.get("id")
        if isinstance(technology_id, str):
            row["name_key"] = technology_id
            titles = _localized_values(module, technology_id)
            descriptions = _localized_values(module, f"{technology_id}_desc")
            if titles:
                row["localized_titles"] = titles
            if descriptions:
                row["localized_descriptions"] = descriptions
        previews = tuple(module.source_slots.get("preview", ()))
        if len(previews) > 1:
            raise ValueError(f"PIHC3 technology module {module.module_id!r} owns more than one preview image.")
        if previews:
            row["image_path"] = context.module_source_path(module, previews[0])
        nodes.append(row)
    payload = dict(projection)
    payload["source_kind"] = "pihc3_technology_modules"
    payload["nodes"] = nodes
    payload["module_ids"] = sorted(module.module_id for module in context.modules if isinstance(module.module_id, str))
    payload["support_module_ids"] = list(support_modules)
    summary = projection.get("summary")
    if isinstance(summary, Mapping):
        payload["summary"] = {
            **summary,
            "module_count": len(context.modules),
            "support_module_count": len(support_modules),
        }
    return payload


def _technology_plan(
    context: ModuleDiagramContext,
    position_intents: Sequence[Mapping[str, object]],
    edge_intents: Sequence[Mapping[str, object]],
) -> Mapping[str, object]:
    sources, _owners, _support_modules = _technology_sources(context)
    return plan_technology_diagram_edits(
        sources,
        position_intents=position_intents,
        edge_intents=edge_intents,
    )


def _technology_node_plan(
    context: ModuleDiagramContext,
    intent: Mapping[str, object],
) -> ModuleDiagramModuleCreation:
    """Resolve one graph intent into the PIHC3 Technology Entity template."""

    technology_id = _required_identifier(intent, "technology_id")
    title = _required_text(intent, "title")
    if "\n" in title or "\r" in title:
        raise ValueError("PIHC3 technology title must fit on one line.")
    description_value = intent.get("description", "")
    if not isinstance(description_value, str):
        raise TypeError("PIHC3 technology creation description must be text.")
    description = description_value.strip()
    folder = _identifier_or_default(
        intent,
        "folder",
        default="support_folder",
    )
    category = _identifier_or_default(
        intent,
        "category",
        default="pihc_all",
    )
    research_cost = _positive_number(intent, "research_cost", default=1.5)
    start_year = _bounded_integer(
        intent,
        "start_year",
        default=1936,
        minimum=1,
        maximum=100_000,
    )
    x = _bounded_integer(
        intent,
        "x",
        default=0,
        minimum=-100_000,
        maximum=100_000,
    )
    y = _bounded_integer(
        intent,
        "y",
        default=0,
        minimum=-100_000,
        maximum=100_000,
    )
    prerequisite_id = _optional_identifier(intent, "prerequisite_id")

    projection = _technology_projection(context)
    nodes = {str(row["id"]): row for row in projection.get("nodes", []) if isinstance(row, Mapping) and isinstance(row.get("id"), str)}
    if technology_id in nodes:
        raise ValueError(f"PIHC3 technology {technology_id!r} already exists.")
    if prerequisite_id is not None and prerequisite_id not in nodes:
        raise ValueError(f"PIHC3 technology prerequisite_id {prerequisite_id!r} must identify an existing technology.")
    folder_sources = [
        {
            "technology_id": str(row["id"]),
            "source_path": row.get("source_path"),
            "source_revision": row.get("source_revision"),
        }
        for row in sorted(
            (value for value in nodes.values() if value.get("folder") == folder),
            key=lambda value: str(value["id"]),
        )
    ]
    prerequisite = nodes.get(prerequisite_id) if prerequisite_id is not None else None
    dependencies = f"dependencies = {{\n\t\t\t{prerequisite_id} = 1\n\t\t}}" if prerequisite_id is not None else ""
    return ModuleDiagramModuleCreation(
        schema="paradev.pihc3.technology-node-module-create.v1",
        family_or_template="technology",
        object_id=technology_id,
        values={
            "title": title,
            "description": description,
            "folder": folder,
            "category": category,
            "research_cost": research_cost,
            "start_year": start_year,
            "x": x,
            "y": y,
            "dependencies": dependencies,
            "language": context.preferred_language,
        },
        intent={
            "technology_id": technology_id,
            "title": title,
            "description": description,
            "folder": folder,
            "category": category,
            "research_cost": research_cost,
            "start_year": start_year,
            "x": x,
            "y": y,
            "prerequisite_id": prerequisite_id,
            "prerequisite_source_revision": (prerequisite.get("source_revision") if isinstance(prerequisite, Mapping) else None),
            "folder_sources": folder_sources,
            "language": context.preferred_language,
        },
    )


_TECHNOLOGY_NODE_AUTHORING = ModuleDiagramNodeAuthoring(
    title="Add PIHC3 technology",
    description=("Create one independently editable Technology module. Selecting a " "technology prefills its tree folder, position, and prerequisite."),
    fields=(
        ModuleDiagramNodeField(
            name="technology_id",
            label="Technology ID",
            required=True,
            description="Stable game identifier, for example TECH_NEW_RADAR.",
        ),
        ModuleDiagramNodeField(name="title", label="Name", required=True),
        ModuleDiagramNodeField(
            name="description",
            label="Description",
            kind="textarea",
        ),
        ModuleDiagramNodeField(
            name="folder",
            label="Technology folder",
            default="support_folder",
        ),
        ModuleDiagramNodeField(
            name="category",
            label="Research category",
            default="pihc_all",
            advanced=True,
        ),
        ModuleDiagramNodeField(
            name="research_cost",
            label="Research cost",
            kind="number",
            default=1.5,
            advanced=True,
        ),
        ModuleDiagramNodeField(
            name="start_year",
            label="Start year",
            kind="number",
            default=1936,
            advanced=True,
        ),
        ModuleDiagramNodeField(name="x", label="X position", kind="number", default=0),
        ModuleDiagramNodeField(name="y", label="Y position", kind="number", default=0),
        ModuleDiagramNodeField(
            name="prerequisite_id",
            label="Prerequisite",
            advanced=True,
        ),
    ),
    selection_defaults=(
        ModuleDiagramSelectionDefault(field="folder", source="folder"),
        ModuleDiagramSelectionDefault(field="prerequisite_id", source="id"),
        ModuleDiagramSelectionDefault(field="x", source="x"),
        ModuleDiagramSelectionDefault(field="y", source="y", offset=2),
    ),
    requires_selection=False,
)


def diagram_provider() -> ModuleDiagramProvider:
    """Return the PIHC3-owned technology-tree authoring provider."""

    return replace(
        TECHNOLOGY_DIAGRAM_PROVIDER,
        project=_technology_projection,
        plan=_technology_plan,
        node_plan=_technology_node_plan,
        node_authoring=_TECHNOLOGY_NODE_AUTHORING,
        authoring_kind="diagram-node",
        selection_defaults=(),
        replaces_registered_provider=True,
    )
