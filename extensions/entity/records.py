"""Strict portable record contract for PIHC3 Entity authoring."""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

from heavenbase.utils import loads_json, validate_json

ASSIGNMENT_CONTRACT = "pihc2.entity.assignments.v1"
RECORD_CONTRACT = "pihc2.entity.record.v1"
RECORD_KEY_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*(?:__D[1-9][0-9]*)?$")
RECORD_ENTITY_FIELDS = frozenset(
    {"apply", "attach", "clone", "default_state", "name", "pdxmesh", "scale", "state"}
)
RECORD_FIELD_LABELS = {
    "pdxmesh": "PDX mesh",
    "soundeffect": "Sound effect",
}
MAX_ENTITY_RECORD_FORM_CONTROLS = 192
MAX_ENTITY_RECORD_FORM_SECTIONS = 64
MAX_ENTITY_RECORD_FORM_DEPTH = 12
_MAX_SAFE_JAVASCRIPT_INTEGER = 9_007_199_254_740_991


def load_entity_record(payload: bytes, *, label: str) -> dict[str, Any]:
    """Parse and validate one strict UTF-8 PIHC2 Entity record.

    Args:
        payload (bytes): Raw portable ``record.json`` bytes.
        label (str): Human-readable source identity included in validation
            errors.

    Returns:
        dict[str, Any]: The ordered ``mesh`` and ``entities`` mapping.

    Raises:
        ValueError: If the bytes are not strict duplicate-free JSON or violate
            the portable Entity record schema.
    """

    value = _load_strict_json(payload, label=label, source_kind="PIHC2 entity record")
    if not isinstance(value, dict) or set(value) != {"mesh", "entities"}:
        raise ValueError(
            f"PIHC2 entity record must contain exactly mesh and entities: {label}"
        )
    mesh = value["mesh"]
    if not isinstance(mesh, Mapping):
        raise ValueError(f"PIHC2 entity record mesh must be an object: {label}")
    scale = mesh.get("scale")
    if isinstance(scale, bool) or not isinstance(scale, (int, float)) or scale <= 0:
        raise ValueError(
            f"PIHC2 entity record mesh.scale must be a positive number: {label}"
        )
    entities = value["entities"]
    if (
        not isinstance(entities, list)
        or not entities
        or not all(isinstance(entity, Mapping) and entity for entity in entities)
    ):
        raise ValueError(
            f"PIHC2 entity record entities must be a non-empty list of objects: {label}"
        )
    for entity_index, entity in enumerate(entities):
        for key in entity:
            if not isinstance(key, str) or not RECORD_KEY_RE.fullmatch(key):
                raise ValueError(
                    f"PIHC2 entity record contains an unsafe field at entities[{entity_index}]: {label}: {key!r}"
                )
            field = key.split("__D", 1)[0]
            if field not in RECORD_ENTITY_FIELDS:
                raise ValueError(
                    f"PIHC2 entity record contains an unsupported field at entities[{entity_index}]: {label}: {key!r}"
                )
        _validate_apply_blocks(entity, label=label, entity_index=entity_index)
    return value


def load_entity_assignments(payload: bytes, *, label: str) -> dict[str, Any]:
    """Parse and validate the ordered portable PIHC2 unit-assignment table.

    Args:
        payload (bytes): Raw portable ``.paradev/entities.json`` bytes.
        label (str): Human-readable source identity included in validation
            errors.

    Returns:
        dict[str, Any]: The ordered ``all_tags`` and ``types`` mapping.

    Raises:
        ValueError: If the bytes are not strict duplicate-free JSON or contain
            missing, empty, duplicate, or undeclared assignment values.
    """

    value = _load_strict_json(
        payload, label=label, source_kind="PIHC2 entity assignment table"
    )
    if not isinstance(value, dict) or set(value) != {"all_tags", "types"}:
        raise ValueError(
            f"PIHC2 entity assignment table must contain exactly all_tags and types: {label}"
        )

    all_tags = value["all_tags"]
    if not isinstance(all_tags, list) or not all_tags:
        raise ValueError(
            f"PIHC2 entity assignment table all_tags must be a non-empty string list: {label}"
        )
    if not all(isinstance(tag, str) and tag for tag in all_tags):
        raise ValueError(
            f"PIHC2 entity assignment table all_tags must be a non-empty string list: {label}"
        )
    if len(set(all_tags)) != len(all_tags):
        raise ValueError(
            f"PIHC2 entity assignment table all_tags must not contain duplicates: {label}"
        )

    unit_types = value["types"]
    if not isinstance(unit_types, Mapping) or not unit_types:
        raise ValueError(
            f"PIHC2 entity assignment table types must be a non-empty object: {label}"
        )
    declared_tags = set(all_tags)
    for unit_id, tags in unit_types.items():
        if not isinstance(unit_id, str) or not unit_id:
            raise ValueError(
                f"PIHC2 entity assignment table types keys must be non-empty strings: {label}"
            )
        if (
            not isinstance(tags, list)
            or not tags
            or not all(isinstance(tag, str) and tag for tag in tags)
        ):
            raise ValueError(
                f"PIHC2 entity assignment table types.{unit_id} must be a non-empty string list: {label}"
            )
        if len(set(tags)) != len(tags):
            raise ValueError(
                f"PIHC2 entity assignment table types.{unit_id} must not contain duplicate tags: {label}"
            )
        undeclared = tuple(tag for tag in tags if tag not in declared_tags)
        if undeclared:
            raise ValueError(
                f"PIHC2 entity assignment table types.{unit_id} uses undeclared all_tags values: "
                f"{', '.join(undeclared)}: {label}"
            )
    return value


def entity_record_source_form(
    record: Mapping[str, Any],
) -> dict[str, object] | None:
    """Project one validated Entity record into bounded scalar controls.

    Args:
        record: Value returned by :func:`load_entity_record`.

    Returns:
        A project-owned `paradev.source-form.v1` provider payload, or `None`
        when the record exceeds the novice form complexity bounds.
    """

    sections: list[dict[str, object]] = []
    control_count = 0
    stack: list[tuple[Mapping[str, Any] | list[Any], tuple[str | int, ...], int]] = [
        (record, (), 0)
    ]
    while stack:
        container, parent_path, depth = stack.pop()
        if depth > MAX_ENTITY_RECORD_FORM_DEPTH:
            return None
        items = (
            tuple(container.items())
            if isinstance(container, Mapping)
            else tuple(enumerate(container))
        )
        controls: list[dict[str, object]] = []
        children: list[
            tuple[Mapping[str, Any] | list[Any], tuple[str | int, ...], int]
        ] = []
        for segment, value in items:
            path = (*parent_path, segment)
            if isinstance(value, (Mapping, list)):
                children.append((value, path, depth + 1))
                continue
            control = _entity_record_scalar_control(
                value,
                path=path,
                control_index=control_count,
            )
            if control is None:
                continue
            control_count += 1
            if control_count > MAX_ENTITY_RECORD_FORM_CONTROLS:
                return None
            controls.append(control)
        if controls:
            if len(sections) >= MAX_ENTITY_RECORD_FORM_SECTIONS:
                return None
            sections.append(
                {
                    "id": f"entity-record-section-{len(sections):03d}",
                    "label": _entity_record_path_label(parent_path),
                    "controls": controls,
                }
            )
        stack.extend(reversed(children))

    if not sections:
        return None
    return {
        "contract": RECORD_CONTRACT,
        "label": {
            "default": "Entity record",
            "zh": "实体记录",
        },
        "description": {
            "default": (
                "Edit existing scalar model, state, event, and assignment "
                "values. Use Code to restructure objects or lists."
            ),
            "zh": "编辑现有模型、状态、事件和分配值。请使用代码模式调整对象或列表结构。",
        },
        "sections": sections,
    }


def _entity_record_scalar_control(
    value: object,
    *,
    path: tuple[str | int, ...],
    control_index: int,
) -> dict[str, object] | None:
    if isinstance(value, bool):
        control = "boolean"
    elif isinstance(value, int):
        if abs(value) > _MAX_SAFE_JAVASCRIPT_INTEGER:
            return None
        control = "number"
    elif isinstance(value, float):
        control = "number"
    elif isinstance(value, str):
        control = "text"
    else:
        return None
    return {
        "id": f"entity-record-control-{control_index:03d}",
        "label": _entity_record_segment_label(path[-1]),
        "control": control,
        "value": value,
        "patch": {
            "op": "replace-json-scalar",
            "path": list(path),
        },
    }


def _entity_record_path_label(path: tuple[str | int, ...]) -> str:
    if not path:
        return "Top level"
    return " › ".join(_entity_record_segment_label(segment) for segment in path)


def _entity_record_segment_label(segment: str | int) -> str:
    if isinstance(segment, int):
        return f"Item {segment + 1}"
    base, separator, duplicate = segment.partition("__D")
    label = RECORD_FIELD_LABELS.get(base)
    if label is None:
        words = " ".join(part for part in base.replace("_", " ").split() if part)
        label = words[:1].upper() + words[1:] if words else base
    if separator and duplicate.isdigit():
        return f"{label} ({int(duplicate) + 1})"
    return label


def _load_strict_json(payload: bytes, *, label: str, source_kind: str) -> Any:
    """Return duplicate-free strict JSON while preserving object insertion order."""

    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"{source_kind} is not strict UTF-8: {label}") from exc
    try:
        value = loads_json(
            text,
            restore=False,
            object_pairs_hook=_unique_json_object,
            parse_constant=_reject_json_constant,
        )
        validate_json(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"{source_kind} is not strict duplicate-free JSON: {label}: {exc}"
        ) from exc
    return value


def _validate_apply_blocks(
    entity: Mapping[object, object], *, label: str, entity_index: int
) -> None:
    for key, raw_apply in entity.items():
        if not isinstance(key, str) or key.split("__D", 1)[0] != "apply":
            continue
        if not isinstance(raw_apply, Mapping):
            raise ValueError(
                f"PIHC2 entity record {key} must be an object at entities[{entity_index}]: {label}"
            )
        if set(raw_apply) - {"countries", "tags"}:
            raise ValueError(
                f"PIHC2 entity record {key} contains unsupported fields at entities[{entity_index}]: {label}"
            )
        countries = raw_apply.get("countries", ["all"])
        tags = raw_apply.get("tags", [])
        if not isinstance(countries, list) or not all(
            isinstance(country, str) and country for country in countries
        ):
            raise ValueError(
                f"PIHC2 entity record {key}.countries must be a string list at entities[{entity_index}]: {label}"
            )
        if not isinstance(tags, list):
            raise ValueError(
                f"PIHC2 entity record {key}.tags must be a list at entities[{entity_index}]: {label}"
            )
        for tag in tags:
            if (
                not isinstance(tag, list)
                or len(tag) != 2
                or not isinstance(tag[0], str)
                or not tag[0]
                or isinstance(tag[1], bool)
                or not isinstance(tag[1], (int, float))
            ):
                raise ValueError(
                    f"PIHC2 entity record {key}.tags must contain [tag, priority] rows at entities[{entity_index}]: {label}"
                )


def _unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON key {key!r}")
        value[key] = item
    return value


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"non-standard JSON constant {value!r}")
