"""Pure deterministic compiler for portable PIHC Entity records."""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Literal

from paradev.pdx import (
    PDXBlock,
    PDXEntry,
    PDXScalar,
    SCALAR_BOOL,
    SCALAR_COLOR,
    SCALAR_ID,
    SCALAR_NUM,
    SCALAR_STR,
    SCALAR_VAR,
)

PRODUCTION_RECORD_COUNT = 134
ROOT_MESH_PATH = "gfx/models/00_hoi4dev_meshes.gfx"
ROOT_ENTITY_PATH = "gfx/models/z_hoi4dev_entities.asset"
ROOT_UNIT_ENTITY_PATH = "gfx/models/zz_hoi4dev_units_entities.asset"

_IDENTIFIER_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")
_OWNER_PART_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
_VARIANT_RE = re.compile(r"^[A-Z0-9][A-Z0-9_]*$")
_MISSING = object()


class EntityCompileError(ValueError):
    """Semantic compiler failure carrying its authoritative input source."""

    def __init__(
        self,
        message: str,
        *,
        source_kind: Literal["assignment", "record", "static"],
        identifier: str | None = None,
    ) -> None:
        super().__init__(message)
        self.source_kind = source_kind
        self.identifier = identifier


@dataclass(frozen=True, slots=True)
class EntityRecordInput:
    """One validated portable Entity source record.

    Attributes:
        identifier (str): Safe generated Entity identifier.
        model_owner (str): Portable aggregate model namespace below
            ``gfx/models``.
        variant_id (str): ``base`` or the uppercase direct-child variant
            identifier.
        source_order (int): Stable zero-based record order.
        value (Mapping[str, Any]): Validated ``mesh`` and ``entities`` record
            mapping.
    """

    identifier: str
    model_owner: str
    variant_id: str
    source_order: int
    value: Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class EntityCompiledFile:
    """One deterministic PDX output owned by the aggregate Entity module.

    Attributes:
        path (str): Portable output path relative to the mod root.
        block (PDXBlock): Ordered compiled PDX syntax tree.
    """

    path: str
    block: PDXBlock


@dataclass(frozen=True, slots=True)
class EntityCompileResult:
    """Compiled files plus source provenance and semantic output counts.

    Attributes:
        files (tuple[EntityCompiledFile, ...]): Deterministically ordered
            compiled PDX files.
        provenance (Mapping[str, tuple[str, ...]]): Output-path mapping to
            contributing record identifiers.
        record_count (int): Number of portable records consumed.
        model_owner_count (int): Number of distinct model namespaces consumed.
        assignment_type_count (int): Number of unit assignment types consumed.
        mesh_count (int): Number of generated ``pdxmesh`` blocks.
        entity_count (int): Number of generated concrete entity blocks.
        unit_entity_count (int): Number of generated country/unit clone blocks.
    """

    files: tuple[EntityCompiledFile, ...]
    provenance: Mapping[str, tuple[str, ...]]
    record_count: int
    model_owner_count: int
    assignment_type_count: int
    mesh_count: int
    entity_count: int
    unit_entity_count: int

    @property
    def file_map(self) -> Mapping[str, PDXBlock]:
        """Return an immutable path-to-block view.

        Returns:
            Mapping[str, PDXBlock]: A read-only mapping preserving ``files``
            insertion order.
        """

        return MappingProxyType({item.path: item.block for item in self.files})


def compile_entity(
    *,
    records: Sequence[EntityRecordInput],
    assignments: Mapping[str, Any],
    asset_paths: Iterable[str],
) -> EntityCompileResult:
    """Compile portable Entity records without reading files or mutating inputs.

    Args:
        records (Sequence[EntityRecordInput]): Portable record values with
            explicit source identity and order.
        assignments (Mapping[str, Any]): Ordered ``all_tags`` and ``types``
            assignment mapping.
        asset_paths (Iterable[str]): Portable aggregate static-asset paths used
            for validation, animation discovery, and texture fallback selection.

    Returns:
        EntityCompileResult: All deterministic aggregate PDX outputs and their
        semantic counts.

    Raises:
        ValueError: If identities, ordering, assignments, assets, record values,
            references, or generated names violate the PIHC2 contract.
    """

    ordered_records = _ordered_records(records)
    all_tags, assignment_types = _assignment_contract(assignments)
    declared_tags = frozenset(all_tags)
    static_paths = _static_paths(asset_paths)
    owners = _model_owners(ordered_records, static_paths)

    animation_by_owner = {
        owner: _owner_animations(owner, static_paths) for owner in owners
    }
    animation_files = tuple(
        EntityCompiledFile(
            path=_animation_path(owner),
            block=_animation_block(owner, animation_by_owner[owner]),
        )
        for owner in owners
    )

    mesh_entries: list[PDXEntry] = []
    entity_entries: list[PDXEntry] = []
    mesh_names: set[str] = set()
    entity_names: set[str] = set()
    tag_candidates: dict[str, dict[str, list[tuple[int | float, str]]]] = {}
    owner_sources: dict[str, list[str]] = {owner: [] for owner in owners}

    for source in ordered_records:
        owner_sources[source.model_owner].append(source.identifier)
        mesh, entities = _record_value(source)
        model_tag = _model_tag(source.model_owner)
        animations = animation_by_owner[source.model_owner]
        mesh_name = f"{source.identifier}_mesh"
        if mesh_name in mesh_names:
            raise EntityCompileError(
                f"PIHC2 Entity compiler generated a duplicate mesh name: {mesh_name!r}.",
                source_kind="record",
                identifier=source.identifier,
            )
        mesh_names.add(mesh_name)
        mesh_entries.append(
            PDXEntry.kv(
                "pdxmesh",
                _mesh_block(
                    source=source,
                    model_tag=model_tag,
                    mesh=mesh,
                    animations=animations,
                    static_paths=static_paths,
                ),
            )
        )
        for entity in entities:
            compiled_entity, entity_name, apply = _entity_block(
                source=source, model_tag=model_tag, entity=entity
            )
            if entity_name in entity_names:
                raise EntityCompileError(
                    f"PIHC2 Entity compiler generated a duplicate entity name: {entity_name!r}.",
                    source_kind="record",
                    identifier=source.identifier,
                )
            entity_names.add(entity_name)
            entity_entries.append(PDXEntry.kv("entity", compiled_entity))
            _collect_candidates(
                tag_candidates,
                entity_name=entity_name,
                apply=apply,
                declared_tags=declared_tags,
                source_identifier=source.identifier,
            )

    selected = _selected_entities(tag_candidates)
    unit_entries = _unit_entity_entries(selected, assignment_types)
    all_identifiers = tuple(source.identifier for source in ordered_records)
    root_files = (
        EntityCompiledFile(
            path=ROOT_MESH_PATH,
            block=PDXBlock.from_entries(
                (PDXEntry.kv("objectTypes", PDXBlock.from_entries(mesh_entries)),)
            ),
        ),
        EntityCompiledFile(
            path=ROOT_ENTITY_PATH, block=PDXBlock.from_entries(entity_entries)
        ),
        EntityCompiledFile(
            path=ROOT_UNIT_ENTITY_PATH, block=PDXBlock.from_entries(unit_entries)
        ),
    )
    files = (*animation_files, *root_files)
    provenance = {
        **{_animation_path(owner): tuple(owner_sources[owner]) for owner in owners},
        ROOT_MESH_PATH: all_identifiers,
        ROOT_ENTITY_PATH: all_identifiers,
        ROOT_UNIT_ENTITY_PATH: all_identifiers,
    }
    return EntityCompileResult(
        files=files,
        provenance=MappingProxyType(provenance),
        record_count=len(ordered_records),
        model_owner_count=len(owners),
        assignment_type_count=len(assignment_types),
        mesh_count=len(mesh_entries),
        entity_count=len(entity_entries),
        unit_entity_count=len(unit_entries),
    )


def canonical_pdx(block: PDXBlock) -> tuple[object, ...]:
    """Return an ordered structural projection without formatting metadata.

    Args:
        block (PDXBlock): Parsed or generated PDX block to project.

    Returns:
        tuple[object, ...]: A recursive tuple that preserves entry and
        duplicate-key order while omitting source formatting metadata.
    """

    return tuple(_canonical_entry(entry) for entry in block.entries)


def _ordered_records(
    records: Sequence[EntityRecordInput],
) -> tuple[EntityRecordInput, ...]:
    if not records:
        raise EntityCompileError(
            "PIHC2 Entity compiler requires at least one record.",
            source_kind="record",
        )
    for source in records:
        if isinstance(source.source_order, bool) or not isinstance(
            source.source_order, int
        ):
            raise EntityCompileError(
                f"PIHC2 Entity record order must be an integer: {source.identifier!r}.",
                source_kind="record",
                identifier=source.identifier,
            )
    ordered = tuple(sorted(records, key=lambda source: source.source_order))
    orders: list[int] = []
    identifiers: set[str] = set()
    variants: set[tuple[str, str]] = set()
    for source in ordered:
        orders.append(source.source_order)
        if not _IDENTIFIER_RE.fullmatch(source.identifier):
            raise EntityCompileError(
                f"PIHC2 Entity record identifier is unsafe: {source.identifier!r}.",
                source_kind="record",
                identifier=source.identifier,
            )
        if source.identifier in identifiers:
            raise EntityCompileError(
                f"PIHC2 Entity record identifier is duplicated: {source.identifier!r}.",
                source_kind="record",
                identifier=source.identifier,
            )
        identifiers.add(source.identifier)
        owner_parts = _portable_parts(source.model_owner)
        if owner_parts is None or any(
            not _OWNER_PART_RE.fullmatch(part) for part in owner_parts
        ):
            raise EntityCompileError(
                f"PIHC2 Entity model owner is unsafe: {source.model_owner!r}.",
                source_kind="record",
                identifier=source.identifier,
            )
        if source.variant_id != "base" and not _VARIANT_RE.fullmatch(source.variant_id):
            raise EntityCompileError(
                f"PIHC2 Entity variant is unsafe: {source.variant_id!r}.",
                source_kind="record",
                identifier=source.identifier,
            )
        variant_key = (source.model_owner, source.variant_id)
        if variant_key in variants:
            raise EntityCompileError(
                f"PIHC2 Entity model variant is duplicated: {source.model_owner}/{source.variant_id}.",
                source_kind="record",
                identifier=source.identifier,
            )
        variants.add(variant_key)
        expected_identifier = _model_tag(source.model_owner)
        if source.variant_id != "base":
            expected_identifier = f"{expected_identifier}_{source.variant_id}"
        if source.identifier != expected_identifier:
            raise EntityCompileError(
                f"PIHC2 Entity identifier {source.identifier!r} does not match owner/variant; expected {expected_identifier!r}.",
                source_kind="record",
                identifier=source.identifier,
            )
    if orders != list(range(len(ordered))):
        raise EntityCompileError(
            f"PIHC2 Entity record orders must be contiguous from 0; found {orders!r}.",
            source_kind="record",
        )
    return ordered


def _assignment_contract(
    assignments: Mapping[str, Any],
) -> tuple[tuple[str, ...], tuple[tuple[str, tuple[str, ...]], ...]]:
    if not isinstance(assignments, Mapping) or set(assignments) != {
        "all_tags",
        "types",
    }:
        raise EntityCompileError(
            "PIHC2 Entity assignments must contain exactly all_tags and types.",
            source_kind="assignment",
        )
    raw_all_tags = assignments["all_tags"]
    if not isinstance(raw_all_tags, list) or not all(
        isinstance(tag, str) and tag for tag in raw_all_tags
    ):
        raise EntityCompileError(
            "PIHC2 Entity assignments all_tags must be a non-empty string list.",
            source_kind="assignment",
        )
    all_tags = tuple(raw_all_tags)
    if not all_tags or len(all_tags) != len(set(all_tags)):
        raise EntityCompileError(
            "PIHC2 Entity assignments all_tags must be unique.",
            source_kind="assignment",
        )
    raw_types = assignments["types"]
    if not isinstance(raw_types, Mapping) or not raw_types:
        raise EntityCompileError(
            "PIHC2 Entity assignments types must be a non-empty object.",
            source_kind="assignment",
        )
    types: list[tuple[str, tuple[str, ...]]] = []
    all_tag_set = set(all_tags)
    for unit, raw_tags in raw_types.items():
        if not isinstance(unit, str) or not unit:
            raise EntityCompileError(
                "PIHC2 Entity assignment type names must be non-empty strings.",
                source_kind="assignment",
            )
        if (
            not isinstance(raw_tags, list)
            or not raw_tags
            or not all(isinstance(tag, str) and tag for tag in raw_tags)
        ):
            raise EntityCompileError(
                f"PIHC2 Entity assignment tags must be a non-empty string list: {unit!r}.",
                source_kind="assignment",
            )
        tags = tuple(raw_tags)
        if len(tags) != len(set(tags)):
            raise EntityCompileError(
                f"PIHC2 Entity assignment tags must be unique: {unit!r}.",
                source_kind="assignment",
            )
        unknown = set(tags) - all_tag_set
        if unknown:
            raise EntityCompileError(
                f"PIHC2 Entity assignment uses unknown tags for {unit!r}: {sorted(unknown)!r}.",
                source_kind="assignment",
            )
        types.append((unit, tags))
    return all_tags, tuple(types)


def _static_paths(asset_paths: Iterable[str]) -> frozenset[str]:
    normalized: set[str] = set()
    for raw_path in asset_paths:
        if not isinstance(raw_path, str) or not raw_path:
            raise EntityCompileError(
                "PIHC2 Entity aggregate asset paths must be non-empty strings.",
                source_kind="static",
            )
        if _portable_parts(raw_path) is None:
            raise EntityCompileError(
                f"PIHC2 Entity aggregate asset path is unsafe: {raw_path!r}.",
                source_kind="static",
            )
        canonical = raw_path
        if canonical in normalized:
            raise EntityCompileError(
                f"PIHC2 Entity aggregate asset path is duplicated: {canonical!r}.",
                source_kind="static",
            )
        normalized.add(canonical)
    return frozenset(normalized)


def _model_owners(
    records: tuple[EntityRecordInput, ...], static_paths: frozenset[str]
) -> tuple[str, ...]:
    owners = tuple(dict.fromkeys(source.model_owner for source in records))
    for owner in owners:
        owner_records = tuple(
            source for source in records if source.model_owner == owner
        )
        if sum(source.variant_id == "base" for source in owner_records) != 1:
            raise EntityCompileError(
                f"PIHC2 Entity model owner must have exactly one base record: {owner!r}.",
                source_kind="record",
                identifier=owner_records[0].identifier if owner_records else None,
            )
        mesh_path = f"gfx/models/{owner}/mesh.mesh"
        if mesh_path not in static_paths:
            raise EntityCompileError(
                f"PIHC2 Entity model owner is missing its aggregate mesh asset: {mesh_path!r}.",
                source_kind="static",
            )
    return owners


def _owner_animations(owner: str, static_paths: frozenset[str]) -> tuple[str, ...]:
    prefix = f"gfx/models/{owner}/"
    names = []
    for raw_path in static_paths:
        if not raw_path.startswith(prefix):
            continue
        relative_path = raw_path[len(prefix) :]
        if "/" not in relative_path and relative_path.endswith(".anim"):
            names.append(relative_path)
    return tuple(sorted(names))


def _animation_path(owner: str) -> str:
    return f"gfx/models/{owner}/animations.asset"


def _animation_block(owner: str, animations: tuple[str, ...]) -> PDXBlock:
    model_tag = _model_tag(owner)
    entries = []
    for filename in animations:
        animation_tag = filename.split(".", 1)[0]
        body = PDXBlock.from_entries(
            (
                _quoted_entry("name", f"{model_tag}_{animation_tag}"),
                _quoted_entry("file", filename),
            )
        )
        entries.append(PDXEntry.kv("animation", body))
    return PDXBlock.from_entries(entries)


def _record_value(
    source: EntityRecordInput,
) -> tuple[Mapping[str, Any], tuple[Mapping[str, Any], ...]]:
    if set(source.value) != {"mesh", "entities"}:
        raise EntityCompileError(
            f"PIHC2 Entity record must contain exactly mesh and entities: {source.identifier!r}.",
            source_kind="record",
            identifier=source.identifier,
        )
    mesh = source.value["mesh"]
    entities = source.value["entities"]
    if not isinstance(mesh, Mapping):
        raise EntityCompileError(
            f"PIHC2 Entity mesh must be an object: {source.identifier!r}.",
            source_kind="record",
            identifier=source.identifier,
        )
    if (
        not isinstance(entities, list)
        or not entities
        or not all(isinstance(entity, Mapping) for entity in entities)
    ):
        raise EntityCompileError(
            f"PIHC2 Entity entities must be a non-empty object list: {source.identifier!r}.",
            source_kind="record",
            identifier=source.identifier,
        )
    return mesh, tuple(entities)


def _mesh_block(
    *,
    source: EntityRecordInput,
    model_tag: str,
    mesh: Mapping[str, Any],
    animations: tuple[str, ...],
    static_paths: frozenset[str],
) -> PDXBlock:
    mesh_settings = PDXBlock.from_entries(
        (
            PDXEntry.kv_id(
                "texture_diffuse",
                _texture_name(source, model_tag, "diffuse", static_paths),
            ),
            PDXEntry.kv_id(
                "texture_normal",
                _texture_name(source, model_tag, "normal", static_paths),
            ),
            PDXEntry.kv_id(
                "texture_specular",
                _texture_name(source, model_tag, "spec", static_paths),
            ),
            PDXEntry.kv_id("shader", "PdxMeshAdvanced"),
        )
    )
    entries = [
        _quoted_entry("name", f"{source.identifier}_mesh"),
        _quoted_entry("file", f"gfx/models/{source.model_owner}/mesh.mesh"),
        PDXEntry.kv("meshsettings", mesh_settings),
    ]
    for filename in animations:
        animation_tag = filename.split(".", 1)[0]
        entries.append(
            PDXEntry.kv(
                "animation",
                PDXBlock.from_entries(
                    (
                        _quoted_entry("id", animation_tag),
                        _quoted_entry("type", f"{model_tag}_{animation_tag}"),
                    )
                ),
            )
        )
    entries.extend(_mapping_entries(mesh))
    return PDXBlock.from_entries(entries)


def _texture_name(
    source: EntityRecordInput, model_tag: str, kind: str, static_paths: frozenset[str]
) -> str:
    placeholder = {
        "diffuse": "nodiffuse.dds",
        "normal": "nonormal.dds",
        "spec": "nospec.dds",
    }[kind]
    own_name = f"{source.identifier}_{kind}.dds"
    own_path = f"gfx/models/{source.model_owner}/{own_name}"
    if own_path in static_paths:
        return own_name
    base_name = f"{model_tag}_{kind}.dds"
    base_path = f"gfx/models/{source.model_owner}/{base_name}"
    if base_path in static_paths:
        return base_name
    return placeholder


def _entity_block(
    *,
    source: EntityRecordInput,
    model_tag: str,
    entity: Mapping[str, Any],
) -> tuple[PDXBlock, str, Mapping[str, Any]]:
    raw_apply = entity.get("apply", {})
    if not isinstance(raw_apply, Mapping):
        raise EntityCompileError(
            f"PIHC2 Entity apply must be an object: {source.identifier!r}.",
            source_kind="record",
            identifier=source.identifier,
        )
    raw_name = entity.get("name", "")
    if not isinstance(raw_name, str):
        raise EntityCompileError(
            f"PIHC2 Entity name must be a string: {source.identifier!r}.",
            source_kind="record",
            identifier=source.identifier,
        )
    entity_name = f"{source.identifier}{'_' + raw_name if raw_name else ''}_entity"
    raw_clone = entity.get("clone")
    if raw_clone is not None and not isinstance(raw_clone, (bool, str)):
        raise EntityCompileError(
            f"PIHC2 Entity clone must be a boolean, string, or null: {source.identifier!r}.",
            source_kind="record",
            identifier=source.identifier,
        )
    clone: str | None
    if raw_clone is True:
        clone = f"{source.identifier}_entity"
    elif raw_clone is False:
        clone = f"{model_tag}_entity"
    else:
        clone = raw_clone

    raw_pdxmesh = entity.get("pdxmesh", _MISSING)
    if (
        raw_pdxmesh is not _MISSING
        and raw_pdxmesh is not None
        and not isinstance(raw_pdxmesh, (bool, str))
    ):
        raise EntityCompileError(
            f"PIHC2 Entity pdxmesh must be a boolean, string, or null: {source.identifier!r}.",
            source_kind="record",
            identifier=source.identifier,
        )
    pdxmesh: str | None
    if raw_pdxmesh is True:
        pdxmesh = f"{source.identifier}_mesh"
    elif raw_pdxmesh is False or raw_pdxmesh is None:
        pdxmesh = None
    elif raw_pdxmesh is _MISSING and clone is None:
        pdxmesh = f"{source.identifier}_mesh"
    elif raw_pdxmesh is _MISSING:
        pdxmesh = None
    else:
        pdxmesh = raw_pdxmesh

    entries = [_quoted_entry("name", entity_name)]
    if clone is not None:
        entries.append(
            PDXEntry(key=PDXScalar.id("clone"), op="=", val=_value_scalar(clone))
        )
    if pdxmesh is not None:
        entries.append(_quoted_entry("pdxmesh", pdxmesh))
    entries.extend(
        _mapping_entries(
            {
                key: value
                for key, value in entity.items()
                if key not in {"apply", "name", "clone", "pdxmesh"}
            }
        )
    )
    return PDXBlock.from_entries(entries), entity_name, raw_apply


def _collect_candidates(
    candidates: dict[str, dict[str, list[tuple[int | float, str]]]],
    *,
    entity_name: str,
    apply: Mapping[str, Any],
    declared_tags: frozenset[str],
    source_identifier: str,
) -> None:
    countries = apply.get("countries", ["all"])
    tags = apply.get("tags", [])
    if not isinstance(countries, list) or not all(
        isinstance(country, str) and country for country in countries
    ):
        raise EntityCompileError(
            f"PIHC2 Entity apply countries must be a non-empty string list: {entity_name!r}.",
            source_kind="record",
            identifier=source_identifier,
        )
    if not isinstance(tags, list):
        raise EntityCompileError(
            f"PIHC2 Entity apply tags must be a list: {entity_name!r}.",
            source_kind="record",
            identifier=source_identifier,
        )
    normalized_tags: list[tuple[str, int | float]] = []
    for row in tags:
        if (
            not isinstance(row, list)
            or len(row) != 2
            or not isinstance(row[0], str)
            or not row[0]
            or isinstance(row[1], bool)
            or not isinstance(row[1], (int, float))
        ):
            raise EntityCompileError(
                f"PIHC2 Entity apply tags must contain [tag, priority] rows: {entity_name!r}.",
                source_kind="record",
                identifier=source_identifier,
            )
        if row[0] not in declared_tags:
            raise EntityCompileError(
                f"PIHC2 Entity apply uses an undeclared all_tags value: {entity_name!r}: {row[0]!r}.",
                source_kind="record",
                identifier=source_identifier,
            )
        normalized_tags.append((row[0], row[1]))
    for country in countries:
        for tag, priority in normalized_tags:
            candidates.setdefault(country, {}).setdefault(tag, []).append(
                (priority, entity_name)
            )
            candidates.setdefault("all", {}).setdefault(tag, []).append(
                (-1, entity_name)
            )


def _selected_entities(
    candidates: Mapping[str, Mapping[str, list[tuple[int | float, str]]]],
) -> dict[str, dict[str, str]]:
    selected: dict[str, dict[str, str]] = {}
    for country, tagged in candidates.items():
        for tag, choices in tagged.items():
            if choices:
                selected.setdefault(country, {})[tag] = sorted(
                    choices, key=lambda item: (-item[0], item[1])
                )[0][1]
    return selected


def _unit_entity_entries(
    selected: Mapping[str, Mapping[str, str]],
    assignment_types: tuple[tuple[str, tuple[str, ...]], ...],
) -> list[PDXEntry]:
    entries: list[PDXEntry] = []
    names: set[str] = set()
    for country, tagged in selected.items():
        for unit, tags in assignment_types:
            for tag in reversed(tags):
                entity_name = tagged.get(tag)
                if entity_name is None:
                    continue
                unit_name = f"{country + '_' if country != 'all' else ''}{unit}_entity"
                if unit_name in names:
                    raise EntityCompileError(
                        f"PIHC2 Entity compiler generated a duplicate unit entity name: {unit_name!r}.",
                        source_kind="assignment",
                    )
                names.add(unit_name)
                body = PDXBlock.from_entries(
                    (
                        PDXEntry(
                            key=PDXScalar.id("name"),
                            op="=",
                            val=_value_scalar(unit_name),
                        ),
                        PDXEntry(
                            key=PDXScalar.id("clone"),
                            op="=",
                            val=_value_scalar(entity_name),
                        ),
                    )
                )
                entries.append(PDXEntry.kv("entity", body))
                break
    return entries


def _mapping_entries(value: Mapping[Any, Any]) -> list[PDXEntry]:
    entries: list[PDXEntry] = []
    for raw_key, item in value.items():
        key = _strip_duplicate(str(raw_key))
        if key.startswith("//"):
            continue
        scalar_key = _value_scalar(key)
        if isinstance(item, Mapping):
            entries.append(
                PDXEntry(
                    key=scalar_key,
                    op="=",
                    val=PDXBlock.from_entries(_mapping_entries(item)),
                )
            )
        elif isinstance(item, list):
            entries.append(
                PDXEntry(
                    key=scalar_key,
                    op="=",
                    val=PDXBlock.from_entries(_list_entries(item)),
                )
            )
        elif item is None:
            entries.append(PDXEntry(key=scalar_key))
        else:
            entries.append(PDXEntry(key=scalar_key, op="=", val=_value_scalar(item)))
    return entries


def _list_entries(value: list[Any]) -> list[PDXEntry]:
    entries: list[PDXEntry] = []
    for item in value:
        if isinstance(item, str) and item.startswith("//"):
            continue
        if isinstance(item, Mapping):
            entries.append(PDXEntry(val=PDXBlock.from_entries(_mapping_entries(item))))
        elif isinstance(item, list):
            entries.append(PDXEntry(val=PDXBlock.from_entries(_list_entries(item))))
        else:
            entries.append(PDXEntry(key=_value_scalar(item)))
    return entries


def _strip_duplicate(key: str) -> str:
    return key.split("__D", 1)[0]


def _quoted_entry(key: str, value: str) -> PDXEntry:
    return PDXEntry(
        key=PDXScalar.id(key),
        op="=",
        val=_quoted_scalar(value),
    )


def _value_scalar(value: Any) -> PDXScalar:
    if isinstance(value, bool):
        raw = "yes" if value else "no"
        return PDXScalar(val=raw, raw=raw, type=SCALAR_BOOL)
    if isinstance(value, (int, float)):
        raw = str(value)
        return PDXScalar(val=raw, raw=raw, type=SCALAR_NUM)
    if not isinstance(value, str):
        raw = str(value)
        return PDXScalar(val=raw, raw=raw, type=SCALAR_ID)
    if value.startswith("``") and value.endswith("``"):
        value = value[2:-2]
        return _quoted_scalar(value)
    if value == "":
        return _quoted_scalar(value)
    must_quote = any(
        mark in value for mark in (" ", "\t", "\n", "'", '"', "/", "[", "]")
    )
    quote_excluded = (
        value.startswith(("rgb", "hsv"))
        or "^" in value
        or re.fullmatch(r"\d{2}:\d{2}", value) is not None
        or value.endswith("%")
        or (value.startswith("[") and value.endswith("]"))
    )
    if must_quote and not quote_excluded:
        return _quoted_scalar(value)
    if value.startswith("@"):
        return PDXScalar(val=value, raw=value, type=SCALAR_VAR)
    if re.match(r"^(rgb|hsv)\s*\{", value, re.IGNORECASE):
        return PDXScalar(val=value, raw=value, type=SCALAR_COLOR)
    return PDXScalar(val=value, raw=value, type=SCALAR_ID)


def _quoted_scalar(value: str) -> PDXScalar:
    rendered = repr(value)
    if rendered.startswith("'") and rendered.endswith("'"):
        inner = rendered[1:-1].replace('"', '\\"').replace("\\'", "'")
        rendered = f'"{inner}"'
    return PDXScalar(val=rendered[1:-1], raw=rendered, type=SCALAR_STR)


def _model_tag(owner: str) -> str:
    return "_".join(owner.split("/")).upper()


def _portable_parts(value: str) -> tuple[str, ...] | None:
    if (
        not value
        or value.startswith("/")
        or value.endswith("/")
        or "//" in value
        or "\\" in value
    ):
        return None
    parts = tuple(value.split("/"))
    return None if any(part in {"", ".", ".."} for part in parts) else parts


def _canonical_entry(entry: PDXEntry) -> tuple[object, ...]:
    return (
        "entry",
        _canonical_scalar(entry.key),
        entry.op,
        canonical_pdx(entry.val)
        if isinstance(entry.val, PDXBlock)
        else _canonical_scalar(entry.val),
    )


def _canonical_scalar(value: PDXScalar | None) -> tuple[str, Any] | None:
    if value is None:
        return None
    return value.type, value.val
