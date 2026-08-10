"""PIHC entity build family with novice-starter asset validation."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass, replace
from typing import ClassVar

import heavenbase as hb
from heavenbase.utils import load_bin, pj
from heavenbase.utils.hash import sha256

from paradev.build import (
    Artifact,
    BuildContext,
    BuildRegistry,
    Collection,
    Diagnostic,
    FamilyCompileResult,
    FamilyNormalizeResult,
    Module,
    ModuleSourceBundle,
    RoutedSourceFamily,
    Slot,
    SourceRoute,
)
from paradev.pdx import PDXBlock, PDXScalar

from .compiler import (
    PRODUCTION_RECORD_COUNT,
    ROOT_MESH_PATH,
    ROOT_UNIT_ENTITY_PATH,
    EntityCompileError,
    EntityCompileResult,
    EntityRecordInput,
    compile_entity,
)
from .records import (
    ASSIGNMENT_CONTRACT,
    RECORD_CONTRACT,
    entity_record_source_form,
    load_entity_assignments,
    load_entity_record,
)

_AUTHORING_CONTRACT = "pihc3.entity.basic.v1"
_BASIC_ROUTE = "basic"
_COMPILED_ROUTE = "compiled_records"
_RECORD_ROUTE = "record"
_ASSIGNMENT_SLOT = "assignment"
_ASSIGNMENT_PATH = ".paradev/entities.json"
_RECORD_SLOT = "record"
_RECORD_PATH = "record.json"
_COPY_SOURCE_SLOTS = ("animations", "meshes", "textures")
_COMPILER_CONTRACT = "pihc3.entity.compiler.v1"
_PRODUCTION_PDX_COUNT = 9
_PRODUCTION_STATIC_PATH_COUNT = 173
_PRODUCTION_STATIC_PATHS_SHA256 = "31cabe822cd1a6952896be9616c3dbde31a6b4ddc9a3e63ff4994f5820986825"
_ENTITY_IDENTIFIER_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")
_MODEL_OWNER_PART_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
_VARIANT_RE = re.compile(r"^[A-Z0-9][A-Z0-9_]*$")
_RECORD_VARIANT_SUFFIX_RE = re.compile(r"^(?P<owner>[A-Z][A-Z0-9_]*?)_(?P<variant>C[0-9]+)$")
_PDXASSETI_V2_HEADER = b"@@b@!\x08pdxasseti\x02\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00"
_PDXASSETI_MARKERS: Mapping[str, tuple[bytes, ...]] = {
    "mesh": (
        b"[object\x00",
        b"[[[mesh\x00",
        b"[[[[aabb\x00",
        b"[[[[material\x00",
        b"[locator\x00",
    ),
    "animation": (b"[info\x00", b"[samples\x00"),
}


@dataclass(frozen=True, slots=True)
class _EntityCompilerInputs:
    """Validated compiler values plus filesystem provenance."""

    aggregate: Module
    record_values: tuple[EntityRecordInput, ...]
    assignments: Mapping[str, object]
    asset_paths: tuple[str, ...]
    record_sources: tuple[tuple[str, str], ...]
    assignment_path: str
    assignment_source: str
    static_sources: tuple[tuple[str, str], ...]


@dataclass(frozen=True, slots=True)
class _EntityCompilation:
    """One successful compiler result with its explicit inputs."""

    inputs: _EntityCompilerInputs
    result: EntityCompileResult


class EntityFamily:
    """Compile model paths and require referenced starter binaries."""

    family_kind: ClassVar[str] = "routed_source"
    family: ClassVar[str] = "entity"
    settings_key: ClassVar[str] = "asset_kind"
    routes: ClassVar[Mapping[str, SourceRoute]] = {
        _BASIC_ROUTE: SourceRoute(
            pdx_path_template="{source_path}",
            copy_path_template="{source_path}",
        ),
        _COMPILED_ROUTE: SourceRoute(copy_path_template="{source_path}"),
        _RECORD_ROUTE: SourceRoute(emits_artifacts=False),
    }
    generated_outputs: ClassVar[tuple[Mapping[str, object], ...]] = (
        {
            "artifact_type": "pdx",
            "owner_kinds": ("module",),
            "route": _COMPILED_ROUTE,
            "target_root": "output",
        },
    )
    source_slots: ClassVar[tuple[Slot, ...]] = (
        Slot(
            name="pdx",
            match=r"^gfx/models/.*\.(gfx|asset)$",
            regex=True,
            kind="pdx",
            many=True,
        ),
        Slot(
            name="meshes",
            match=r"^gfx/models/.*\.mesh$",
            regex=True,
            kind="copy",
            many=True,
            authoring_path="gfx/models/{object_id}/{filename}",
        ),
        Slot(
            name="animations",
            match=r"^gfx/models/.*\.anim$",
            regex=True,
            kind="copy",
            many=True,
            authoring_path="gfx/models/{object_id}/{filename}",
        ),
        Slot(
            name="textures",
            match=r"^gfx/models/.*\.(dds|png|tga)$",
            regex=True,
            kind="copy",
            many=True,
            authoring_path="gfx/models/{object_id}/{filename}",
        ),
        Slot(name=_ASSIGNMENT_SLOT, match=_ASSIGNMENT_PATH),
        Slot(name=_RECORD_SLOT, match=_RECORD_PATH),
    )
    metadata_keys: ClassVar[tuple[str, ...]] = ()
    settings_keys: ClassVar[tuple[str, ...]] = (
        "animation_file",
        "authoring_contract",
        "mesh_file",
        "model_owner",
        "source_order",
        "variant_id",
    )
    settings_values: ClassVar[Mapping[str, tuple[str, ...]]] = {
        "authoring_contract": (_AUTHORING_CONTRACT,),
    }
    required_settings: ClassVar[tuple[str, ...]] = ()
    required_loc_keys: ClassVar[tuple[str, ...]] = ()
    asset_constraints: ClassVar[Mapping[str, Mapping[str, object]]] = {}
    default_assets: ClassVar[Mapping[str, Mapping[str, object]]] = {}
    settings_normalizers: ClassVar[Mapping[str, object]] = {}
    sprite_gfx_path_template: ClassVar[str | None] = None
    sprite_name_template: ClassVar[str | None] = None
    sprite_slots: ClassVar[tuple[str, ...]] = ()

    def source_form(
        self,
        *,
        module_id: str,
        relative_path: str,
        text: str,
    ) -> dict[str, object] | None:
        """Return the project-owned guided form for one Entity record."""

        if relative_path != _RECORD_PATH:
            return None
        record = load_entity_record(
            text.encode("utf-8"),
            label=f"{module_id}/{relative_path}",
        )
        return entity_record_source_form(record)

    def validate_source_text(
        self,
        *,
        module_id: str,
        relative_path: str,
        text: str,
    ) -> None:
        """Validate editable text owned by the PIHC3 Entity compiler.

        Args:
            module_id (str): ParaDev module identifier used to label validation
                errors.
            relative_path (str): Module-relative source path selected for the
                draft write.
            text (str): Proposed UTF-8 source text.

        Returns:
            None: This method does not return a value.

        Raises:
            ValueError: If a compiler-owned record or assignment source is
                malformed or violates its portable schema.
        """

        label = f"{module_id}/{relative_path}"
        if relative_path == _RECORD_PATH:
            load_entity_record(text.encode("utf-8"), label=label)
        elif relative_path == _ASSIGNMENT_PATH:
            load_entity_assignments(text.encode("utf-8"), label=label)

    def normalize(
        self,
        ctx: BuildContext,
        modules: tuple[Module, ...],
        collections: tuple[Collection, ...],
    ) -> FamilyNormalizeResult:
        """Derive compiler routes and record identity from source structure."""

        normalized = _modules_with_inferred_settings(modules)
        return _delegate().normalize(ctx, normalized, collections)

    def check(
        self,
        ctx: BuildContext,
        modules: tuple[Module, ...],
        collections: tuple[Collection, ...],
    ) -> tuple[Diagnostic, ...]:
        """Return route-specific source and starter asset diagnostics."""

        diagnostics = list(_route_diagnostics(ctx, modules, collections))
        compiler_diagnostics, _compilation = _compiler_plan(
            modules,
            prior=tuple(diagnostics),
        )
        diagnostics.extend(compiler_diagnostics)
        return tuple(diagnostics)

    def compile(
        self,
        ctx: BuildContext,
        modules: tuple[Module, ...],
        collections: tuple[Collection, ...],
    ) -> FamilyCompileResult:
        """Validate and emit from one shared Entity compiler preparation."""

        diagnostics = list(_route_diagnostics(ctx, modules, collections))
        compiler_diagnostics, compilation = _compiler_plan(
            modules,
            prior=tuple(diagnostics),
        )
        diagnostics.extend(compiler_diagnostics)
        delegated = _delegate().emit(ctx, modules, collections)
        return FamilyCompileResult(
            artifacts=_entity_artifacts(delegated, modules, compilation),
            diagnostics=tuple(diagnostics),
        )

    def emit(
        self,
        ctx: BuildContext,
        modules: tuple[Module, ...],
        collections: tuple[Collection, ...],
    ) -> tuple[Artifact, ...]:
        """Emit compiler-owned aggregate PDX and path-preserving assets."""

        delegated = _delegate().emit(ctx, modules, collections)
        diagnostics = _route_diagnostics(ctx, modules, collections)
        _diagnostics, compilation = _compiler_plan(
            modules,
            prior=diagnostics,
        )
        return _entity_artifacts(delegated, modules, compilation)


def register(registry: BuildRegistry) -> BuildRegistry:
    """Register the project-local PIHC entity family."""

    return registry.add(EntityFamily())


class PIHC3ModelEntity(hb.Entity):
    """PIHC3 model Entity record with its portable compiler contract."""

    identifier = "pihc3-model-entity"

    record_id = hb.field(hb.ShortText).desc("Stable generated model Entity identifier.")
    model_owner = hb.field(hb.ShortText).default("").desc("Portable model namespace.")
    variant_id = hb.field(hb.ShortText).default("base").desc("Model variant identifier.")
    definition = hb.field(hb.Json).default({}).desc("Portable mesh and concrete Entity record.")
    assignments = hb.field(hb.Json).default({}).desc("Optional aggregate unit assignment table.")
    assets = hb.field(hb.Json).default([]).desc("Module-relative mesh, animation, and texture paths.")

    family = EntityFamily.family
    resource_slots = EntityFamily.source_slots
    compilation_hooks = (
        "validate_source_text",
        "normalize",
        "compile",
        "check",
        "emit",
    )

    @classmethod
    def build_family(cls) -> EntityFamily:
        """Return the portable compiler owned by this Entity type."""

        return EntityFamily()


def _route_diagnostics(
    ctx: BuildContext,
    modules: tuple[Module, ...],
    collections: tuple[Collection, ...],
) -> tuple[Diagnostic, ...]:
    diagnostics = list(_delegate().check(ctx, modules, collections))
    for module in modules:
        route = _module_route(module)
        if route == _BASIC_ROUTE:
            diagnostics.extend(_basic_route_diagnostics(module))
            diagnostics.extend(_starter_asset_diagnostics(module))
        elif route == _COMPILED_ROUTE:
            diagnostics.extend(_compiled_route_diagnostics(module))
        elif route == _RECORD_ROUTE:
            diagnostics.extend(_record_diagnostics(module))
    diagnostics.extend(_duplicate_record_order_diagnostics(modules))
    return tuple(diagnostics)


def _delegate() -> RoutedSourceFamily:
    return RoutedSourceFamily(
        family=EntityFamily.family,
        routes=EntityFamily.routes,
        settings_key=EntityFamily.settings_key,
        source_slots=EntityFamily.source_slots,
        metadata_keys=EntityFamily.metadata_keys,
        settings_keys=EntityFamily.settings_keys,
        settings_values=EntityFamily.settings_values,
        required_settings=EntityFamily.required_settings,
        required_loc_keys=EntityFamily.required_loc_keys,
        asset_constraints=EntityFamily.asset_constraints,
        default_assets=EntityFamily.default_assets,
        settings_normalizers=EntityFamily.settings_normalizers,
        sprite_gfx_path_template=EntityFamily.sprite_gfx_path_template,
        sprite_name_template=EntityFamily.sprite_name_template,
        sprite_slots=EntityFamily.sprite_slots,
    )


def _module_route(module: Module) -> str | None:
    settings = module.metadata.get("settings")
    if not isinstance(settings, Mapping):
        return None
    route = settings.get(EntityFamily.settings_key)
    return route.strip() if isinstance(route, str) and route.strip() else None


def _modules_with_inferred_settings(modules: tuple[Module, ...]) -> tuple[Module, ...]:
    record_modules = tuple(
        sorted(
            (module for module in modules if _module_has_slot(module, _RECORD_SLOT)),
            key=lambda module: module.module_id,
        )
    )
    record_order = {module.module_id: source_order for source_order, module in enumerate(record_modules)}
    return tuple(_module_with_inferred_settings(module, record_order=record_order) for module in modules)


def _module_with_inferred_settings(
    module: Module,
    *,
    record_order: Mapping[str, int],
) -> Module:
    settings = module.metadata.get("settings")
    normalized_settings = dict(settings) if isinstance(settings, Mapping) else {}
    if module.module_id in record_order:
        object_id = module.module_id.rsplit("/", 1)[-1]
        owner_id, variant_id = _record_identity_from_object_id(object_id)
        normalized_settings.update(
            {
                EntityFamily.settings_key: _RECORD_ROUTE,
                "model_owner": owner_id.casefold().replace("_", "/"),
                "source_order": record_order[module.module_id],
                "variant_id": variant_id,
            }
        )
    elif module.module_id == "entity/HOI4DEV_ENTITIES" and _module_has_slot(module, _ASSIGNMENT_SLOT):
        normalized_settings[EntityFamily.settings_key] = _COMPILED_ROUTE
    else:
        normalized_settings.setdefault(EntityFamily.settings_key, _BASIC_ROUTE)
    metadata = dict(module.metadata)
    metadata["settings"] = normalized_settings
    payload = module.payload
    if isinstance(payload, ModuleSourceBundle):
        payload = replace(payload, metadata=dict(metadata))
    return replace(module, metadata=metadata, payload=payload)


def _module_has_slot(module: Module, slot: str) -> bool:
    return bool(_module_bundle(module).source_slots.get(slot))


def _record_identity_from_object_id(object_id: str) -> tuple[str, str]:
    match = _RECORD_VARIANT_SUFFIX_RE.fullmatch(object_id)
    if match is None:
        return object_id, "base"
    return match.group("owner"), match.group("variant")


def _basic_route_diagnostics(module: Module) -> tuple[Diagnostic, ...]:
    bundle = _module_bundle(module)
    diagnostics: list[Diagnostic] = []
    if not bundle.source_slots.get("pdx"):
        diagnostics.append(
            _route_diagnostic(
                module,
                code="entity.missing_pdx_source",
                message="basic Entity modules must contain at least one matched PDX definition.",
                slot="pdx",
                source_path="gfx/models",
            )
        )
    for source_path in bundle.source_slots.get(_RECORD_SLOT, ()):
        diagnostics.append(
            _route_diagnostic(
                module,
                code="entity.unexpected_record_source",
                message="basic Entity modules cannot contain aggregate record.json sources.",
                slot=_RECORD_SLOT,
                source_path=source_path,
            )
        )
    for source_path in bundle.source_slots.get(_ASSIGNMENT_SLOT, ()):
        diagnostics.append(
            _route_diagnostic(
                module,
                code="entity.unexpected_assignment_source",
                message="basic Entity modules cannot contain an aggregate assignment source.",
                slot=_ASSIGNMENT_SLOT,
                source_path=source_path,
            )
        )
    return tuple(diagnostics)


def _compiled_route_diagnostics(module: Module) -> tuple[Diagnostic, ...]:
    bundle = _module_bundle(module)
    diagnostics: list[Diagnostic] = []
    if module.module_id != "entity/HOI4DEV_ENTITIES":
        diagnostics.append(
            _route_diagnostic(
                module,
                code="entity.invalid_compiler_aggregate",
                message="compiled-records routing is reserved for entity/HOI4DEV_ENTITIES.",
                slot=_ASSIGNMENT_SLOT,
                source_path="meta.yaml",
            )
        )
    for source_path in bundle.source_slots.get(_RECORD_SLOT, ()):
        diagnostics.append(
            _route_diagnostic(
                module,
                code="entity.unexpected_record_source",
                message="the compiled-records aggregate cannot contain record.json sources.",
                slot=_RECORD_SLOT,
                source_path=source_path,
            )
        )
    diagnostics.extend(_assignment_source_diagnostics(module))
    return tuple(diagnostics)


def _assignment_source_diagnostics(module: Module) -> tuple[Diagnostic, ...]:
    bundle = _module_bundle(module)
    assignment_paths = tuple(bundle.source_slots.get(_ASSIGNMENT_SLOT, ()))
    if len(assignment_paths) != 1:
        return (
            _route_diagnostic(
                module,
                code=("entity.missing_assignment_source" if not assignment_paths else "entity.multiple_assignment_sources"),
                message=("the Entity compiler aggregate must contain exactly one " f"{_ASSIGNMENT_PATH} assignment source."),
                slot=_ASSIGNMENT_SLOT,
                source_path=_ASSIGNMENT_PATH,
            ),
        )

    diagnostics: list[Diagnostic] = []
    assignment_path = assignment_paths[0]
    try:
        payload = load_bin(pj(bundle.root, assignment_path), strict=True)
        load_entity_assignments(payload, label=f"{module.module_id}/{assignment_path}")
    except (OSError, ValueError) as exc:
        diagnostics.append(
            _route_diagnostic(
                module,
                code="entity.invalid_assignment_source",
                message=f"aggregate assignment source is invalid: {exc}.",
                slot=_ASSIGNMENT_SLOT,
                source_path=assignment_path,
            )
        )
    return tuple(diagnostics)


def _is_compiler_aggregate(module: Module) -> bool:
    return module.module_id == "entity/HOI4DEV_ENTITIES" and _module_route(module) == _COMPILED_ROUTE


def _compiler_plan(
    modules: tuple[Module, ...],
    *,
    prior: tuple[Diagnostic, ...],
) -> tuple[tuple[Diagnostic, ...], _EntityCompilation | None]:
    """Return compiler diagnostics and the matching prepared compilation."""

    aggregates = tuple(module for module in modules if _is_compiler_aggregate(module))
    records = tuple(module for module in modules if _module_route(module) == _RECORD_ROUTE)
    if not aggregates:
        if len(records) >= PRODUCTION_RECORD_COUNT:
            return (
                (
                    _compiler_diagnostic(
                        records[0],
                        code="entity.compiler_missing_aggregate",
                        message=(
                            "Entity compilation found a complete portable record corpus without "
                            "entity/HOI4DEV_ENTITIES; include the compiler aggregate in the project build."
                        ),
                        source_path="meta.yaml",
                    ),
                ),
                None,
            )
        return (), None
    if len(aggregates) != 1:
        return (
            (
                _compiler_diagnostic(
                    aggregates[0] if aggregates else None,
                    code="entity.compiler_aggregate_count",
                    message=f"Entity compilation requires exactly one compiler aggregate; found {len(aggregates)}.",
                ),
            ),
            None,
        )

    aggregate = aggregates[0]
    compiler_module_ids = {
        aggregate.module_id,
        *(record.module_id for record in records),
    }
    if any(diagnostic.severity == "error" and diagnostic.module_id in compiler_module_ids for diagnostic in prior):
        return (), None
    if len(records) != PRODUCTION_RECORD_COUNT:
        return (
            (
                _compiler_diagnostic(
                    aggregate,
                    code="entity.compiler_incomplete_records",
                    message=(
                        f"Entity compilation requires all {PRODUCTION_RECORD_COUNT} portable records with "
                        f"entity/HOI4DEV_ENTITIES; found {len(records)}. Build the full Entity family."
                    ),
                ),
            ),
            None,
        )

    compiler_inputs: _EntityCompilerInputs | None = None
    try:
        compiler_inputs = _entity_compiler_inputs(aggregate, records)
        compilation = _compile_entity_inputs(compiler_inputs)
    except (IndexError, OSError, TypeError, ValueError) as exc:
        assignment_path = compiler_inputs.assignment_path if compiler_inputs is not None else _ASSIGNMENT_PATH
        source_module: Module = aggregate
        source_path = "meta.yaml"
        source_slot: str | None = _RECORD_SLOT
        source_slots: tuple[str, ...] = ()
        if isinstance(exc, EntityCompileError) and exc.source_kind == "record" and exc.identifier is not None:
            source_module = next(
                (module for module in records if module.module_id.rsplit("/", 1)[-1] == exc.identifier),
                aggregate,
            )
            source_path = "record.json"
            source_slot = _RECORD_SLOT
        elif isinstance(exc, EntityCompileError) and exc.source_kind == "assignment":
            source_path = assignment_path
            source_slot = _ASSIGNMENT_SLOT
        elif isinstance(exc, EntityCompileError) and exc.source_kind == "static":
            source_path = "gfx/models"
            source_slot = None
            source_slots = _COPY_SOURCE_SLOTS
        return (
            (
                _compiler_diagnostic(
                    source_module,
                    code="entity.compiler_failed",
                    message=f"Entity compilation failed: {str(exc).rstrip('.')}.",
                    source_path=source_path,
                    slot=source_slot,
                    slots=source_slots,
                ),
            ),
            None,
        )
    return (), compilation


def _entity_artifacts(
    delegated: tuple[Artifact, ...],
    modules: tuple[Module, ...],
    compilation: _EntityCompilation | None,
) -> tuple[Artifact, ...]:
    """Replace aggregate PDX with compiler output while preserving copy order."""

    compiled_route_modules = tuple(module for module in modules if _module_route(module) == _COMPILED_ROUTE)
    if not compiled_route_modules:
        return delegated

    aggregate_owners = {f"module:{module.module_id}" for module in compiled_route_modules}
    without_aggregate = tuple(artifact for artifact in delegated if artifact.owner not in aggregate_owners)
    if compilation is None:
        return without_aggregate

    owner = f"module:{compilation.inputs.aggregate.module_id}"
    insertion_index = next(
        (index for index, artifact in enumerate(delegated) if artifact.owner == owner),
        len(delegated),
    )
    insertion_index -= sum(artifact.owner in aggregate_owners for artifact in delegated[:insertion_index])
    aggregate_copies = tuple(artifact for artifact in delegated if artifact.owner == owner)
    compiled_artifacts = _compiled_artifacts(compilation)
    return (
        *without_aggregate[:insertion_index],
        *compiled_artifacts,
        *aggregate_copies,
        *without_aggregate[insertion_index:],
    )


def _entity_compiler_inputs(
    aggregate: Module,
    records: tuple[Module, ...],
) -> _EntityCompilerInputs:
    record_values, record_sources = _compiler_record_inputs(records)
    aggregate_bundle = _module_bundle(aggregate)
    assignment_path = tuple(aggregate_bundle.source_slots.get(_ASSIGNMENT_SLOT, ()))[0]
    assignment_source = pj(aggregate_bundle.root, assignment_path)
    assignment_payload = load_bin(assignment_source, strict=True)
    assignments = load_entity_assignments(
        assignment_payload,
        label=f"{aggregate.module_id}/{assignment_path}",
    )
    static_sources = tuple((source.path, pj(aggregate_bundle.root, source.path)) for source in aggregate_bundle.copy_sources)
    _validate_static_inventory(static_sources)
    return _EntityCompilerInputs(
        aggregate=aggregate,
        record_values=record_values,
        assignments=assignments,
        asset_paths=tuple(path for path, _source in static_sources),
        record_sources=record_sources,
        assignment_path=assignment_path,
        assignment_source=assignment_source,
        static_sources=static_sources,
    )


def _validate_static_inventory(static_sources: tuple[tuple[str, str], ...]) -> None:
    relative_paths = tuple(sorted(path for path, _source in static_sources))
    digest = sha256(b"".join(path.encode("utf-8") + b"\0" for path in relative_paths)).hexdigest()
    if len(relative_paths) != _PRODUCTION_STATIC_PATH_COUNT or digest != _PRODUCTION_STATIC_PATHS_SHA256:
        raise EntityCompileError(
            (
                "PIHC Entity compiler aggregate static inventory must preserve exactly "
                f"{_PRODUCTION_STATIC_PATH_COUNT} contracted paths; found {len(relative_paths)} "
                f"with path digest {digest}"
            ),
            source_kind="static",
        )


def _compile_entity_inputs(inputs: _EntityCompilerInputs) -> _EntityCompilation:
    result = compile_entity(
        records=inputs.record_values,
        assignments=inputs.assignments,
        asset_paths=inputs.asset_paths,
    )
    paths = tuple(item.path for item in result.files)
    if len(paths) != _PRODUCTION_PDX_COUNT or len(paths) != len(set(paths)):
        raise ValueError(f"Entity compiler must produce {_PRODUCTION_PDX_COUNT} unique PDX paths; found {len(paths)} files and {len(set(paths))} paths.")
    return _EntityCompilation(inputs=inputs, result=result)


def _compiled_artifacts(compilation: _EntityCompilation) -> tuple[Artifact, ...]:
    owner = f"module:{compilation.inputs.aggregate.module_id}"
    artifacts: list[Artifact] = []
    for compiled_file in sorted(compilation.result.files, key=lambda item: item.path):
        metadata: dict[str, object] = {
            "compiler": _COMPILER_CONTRACT,
            "record_count": len(compilation.result.provenance[compiled_file.path]),
        }
        if compiled_file.path == ROOT_UNIT_ENTITY_PATH:
            metadata["assignment_contract"] = ASSIGNMENT_CONTRACT
        artifacts.append(
            Artifact(
                path=compiled_file.path,
                artifact_type="pdx",
                owner=owner,
                inputs=_compiled_artifact_inputs(compilation, compiled_file.path),
                metadata=metadata,
                payload=compiled_file.block,
            )
        )
    return tuple(artifacts)


def _compiled_artifact_inputs(
    compilation: _EntityCompilation,
    artifact_path: str,
) -> tuple[str, ...]:
    inputs = compilation.inputs
    record_sources = dict(inputs.record_sources)
    sources: list[str] = []
    for identifier in compilation.result.provenance[artifact_path]:
        if identifier not in record_sources:
            raise ValueError(f"Entity compiler provenance references an unknown record: {identifier!r}.")
        sources.append(record_sources[identifier])

    if artifact_path == ROOT_MESH_PATH:
        sources.extend(source_path for relative_path, source_path in inputs.static_sources if relative_path.endswith((".anim", ".dds", ".mesh")))
    elif artifact_path == ROOT_UNIT_ENTITY_PATH:
        sources.append(inputs.assignment_source)
    elif artifact_path.endswith("/animations.asset"):
        owner_prefix = artifact_path.rsplit("/", 1)[0] + "/"
        sources.extend(
            source_path
            for relative_path, source_path in inputs.static_sources
            if relative_path.startswith(owner_prefix) and "/" not in relative_path[len(owner_prefix) :] and relative_path.endswith(".anim")
        )
    return tuple(dict.fromkeys(sources))


def _compiler_record_inputs(
    records: tuple[Module, ...],
) -> tuple[tuple[EntityRecordInput, ...], tuple[tuple[str, str], ...]]:
    rows: list[tuple[EntityRecordInput, str]] = []
    for module in records:
        bundle = _module_bundle(module)
        record_path = tuple(bundle.source_slots.get(_RECORD_SLOT, ()))[0]
        source_path = pj(bundle.root, record_path)
        payload = load_bin(source_path, strict=True)
        value = load_entity_record(payload, label=f"{module.module_id}/{record_path}")
        settings = module.metadata.get("settings")
        settings_map = settings if isinstance(settings, Mapping) else {}
        identifier = module.module_id.rsplit("/", 1)[-1]
        model_owner = settings_map.get("model_owner")
        variant_id = settings_map.get("variant_id")
        source_order = settings_map.get("source_order")
        if not isinstance(model_owner, str) or not isinstance(variant_id, str):
            raise TypeError(f"Entity record {module.module_id} lacks compiler identity metadata.")
        if isinstance(source_order, bool) or not isinstance(source_order, int):
            raise TypeError(f"Entity record {module.module_id} lacks an integer compiler order.")
        record = EntityRecordInput(
            identifier=identifier,
            model_owner=model_owner,
            variant_id=variant_id,
            source_order=source_order,
            value=value,
        )
        rows.append((record, source_path))
    rows.sort(key=lambda row: row[0].source_order)
    return (
        tuple(row[0] for row in rows),
        tuple((row[0].identifier, row[1]) for row in rows),
    )


def _compiler_diagnostic(
    module: Module | None,
    *,
    code: str,
    message: str,
    source_path: str = "meta.yaml",
    slot: str | None = _RECORD_SLOT,
    slots: tuple[str, ...] = (),
) -> Diagnostic:
    return Diagnostic(
        code=code,
        message=message,
        severity="error",
        family=EntityFamily.family,
        module_id=module.module_id if module is not None else None,
        slot=slot,
        slots=slots,
        source_path=source_path,
    )


def _record_diagnostics(module: Module) -> tuple[Diagnostic, ...]:
    bundle = _module_bundle(module)
    record_paths = tuple(bundle.source_slots.get(_RECORD_SLOT, ()))
    diagnostics: list[Diagnostic] = []
    if len(record_paths) != 1:
        diagnostics.append(
            _route_diagnostic(
                module,
                code=("entity.missing_record_source" if not record_paths else "entity.multiple_record_sources"),
                message=(
                    "record Entity modules must contain exactly one record.json source."
                    if not record_paths
                    else "record Entity modules cannot contain more than one record source."
                ),
                slot=_RECORD_SLOT,
                source_path="record.json",
            )
        )
    for slot in ("pdx", _ASSIGNMENT_SLOT, *_COPY_SOURCE_SLOTS):
        for source_path in bundle.source_slots.get(slot, ()):
            source_kind = "PDX" if slot == "pdx" else ("assignment" if slot == _ASSIGNMENT_SLOT else "copied asset")
            diagnostics.append(
                _route_diagnostic(
                    module,
                    code=(
                        "entity.unexpected_record_pdx_source"
                        if slot == "pdx"
                        else ("entity.unexpected_record_assignment_source" if slot == _ASSIGNMENT_SLOT else "entity.unexpected_record_copy_source")
                    ),
                    message=f"record Entity modules cannot contain {source_kind} sources.",
                    slot=slot,
                    source_path=source_path,
                )
            )

    payload: bytes | None = None
    record_path = record_paths[0] if len(record_paths) == 1 else None
    if record_path is not None:
        try:
            payload = load_bin(pj(bundle.root, record_path), strict=True)
        except OSError as exc:
            diagnostics.append(
                _route_diagnostic(
                    module,
                    code="entity.unreadable_record_source",
                    message=f"record source cannot be read: {exc}.",
                    slot=_RECORD_SLOT,
                    source_path=record_path,
                )
            )
        if payload is not None:
            try:
                load_entity_record(payload, label=f"{module.module_id}/{record_path}")
            except ValueError as exc:
                diagnostics.append(
                    _route_diagnostic(
                        module,
                        code="entity.invalid_record_source",
                        message=str(exc),
                        slot=_RECORD_SLOT,
                        source_path=record_path,
                    )
                )
    diagnostics.extend(_record_metadata_diagnostics(module))
    return tuple(diagnostics)


def _record_metadata_diagnostics(module: Module) -> tuple[Diagnostic, ...]:
    settings = module.metadata.get("settings")
    settings_map = settings if isinstance(settings, Mapping) else {}
    diagnostics: list[Diagnostic] = []

    object_id = module.module_id.rsplit("/", 1)[-1]
    if not _ENTITY_IDENTIFIER_RE.fullmatch(object_id):
        diagnostics.append(
            _record_metadata_diagnostic(
                module,
                "module identifier must be safe uppercase Entity text.",
            )
        )

    model_owner = settings_map.get("model_owner")
    owner_parts = _portable_model_owner_parts(model_owner)
    if owner_parts is None:
        diagnostics.append(
            _record_metadata_diagnostic(
                module,
                "settings.model_owner must be a portable lowercase relative model path.",
            )
        )

    variant_id = settings_map.get("variant_id")
    if not isinstance(variant_id, str) or (variant_id != "base" and not _VARIANT_RE.fullmatch(variant_id)):
        diagnostics.append(
            _record_metadata_diagnostic(
                module,
                "settings.variant_id must be 'base' or one safe uppercase direct-child identifier.",
            )
        )

    expected_identifier: str | None = None
    if owner_parts is not None and isinstance(variant_id, str) and (variant_id == "base" or _VARIANT_RE.fullmatch(variant_id)):
        owner_identifier = "_".join(owner_parts).upper()
        expected_identifier = owner_identifier if variant_id == "base" else f"{owner_identifier}_{variant_id}"
    if expected_identifier is not None and object_id != expected_identifier:
        diagnostics.append(
            _record_metadata_diagnostic(
                module,
                f"module identifier must be {expected_identifier!r} for its model owner and variant.",
            )
        )

    source_order = settings_map.get("source_order")
    if isinstance(source_order, bool) or not isinstance(source_order, int) or source_order < 0:
        diagnostics.append(
            _record_metadata_diagnostic(
                module,
                "settings.source_order must be a non-negative integer.",
            )
        )

    return tuple(diagnostics)


def _portable_model_owner_parts(value: object) -> tuple[str, ...] | None:
    if not isinstance(value, str) or not value or "\\" in value or value.startswith("/") or value.endswith("/") or "//" in value:
        return None
    parts = tuple(value.split("/"))
    if len(parts) < 2:
        return None
    if any(part in {"", ".", ".."} or not _MODEL_OWNER_PART_RE.fullmatch(part) for part in parts):
        return None
    return parts


def _duplicate_record_order_diagnostics(
    modules: tuple[Module, ...],
) -> tuple[Diagnostic, ...]:
    by_order: dict[int, list[Module]] = {}
    for module in modules:
        if _module_route(module) != _RECORD_ROUTE:
            continue
        settings = module.metadata.get("settings")
        settings_map = settings if isinstance(settings, Mapping) else {}
        source_order = settings_map.get("source_order")
        if isinstance(source_order, bool) or not isinstance(source_order, int) or source_order < 0:
            continue
        by_order.setdefault(source_order, []).append(module)
    diagnostics: list[Diagnostic] = []
    for source_order, owners in sorted(by_order.items()):
        if len(owners) < 2:
            continue
        owner_ids = ", ".join(sorted(module.module_id for module in owners))
        for module in owners:
            diagnostics.append(
                _record_metadata_diagnostic(
                    module,
                    f"settings.source_order {source_order} is duplicated by: {owner_ids}.",
                )
            )
    return tuple(diagnostics)


def _record_metadata_diagnostic(
    module: Module,
    message: str,
    *,
    source_path: str = "meta.yaml",
) -> Diagnostic:
    return _route_diagnostic(
        module,
        code="entity.invalid_record_metadata",
        message=message,
        slot=_RECORD_SLOT,
        source_path=source_path,
    )


def _route_diagnostic(
    module: Module,
    *,
    code: str,
    message: str,
    slot: str,
    source_path: str,
) -> Diagnostic:
    return Diagnostic(
        code=code,
        message=f"Entity module {module.module_id} {message}",
        severity="error",
        family=EntityFamily.family,
        module_id=module.module_id,
        slot=slot,
        source_path=source_path,
    )


def _starter_asset_diagnostics(module: Module) -> tuple[Diagnostic, ...]:
    settings = module.metadata.get("settings")
    settings_map = settings if isinstance(settings, Mapping) else {}
    bundle = _module_bundle(module)
    if not _is_starter_module(settings_map):
        return ()
    diagnostics: list[Diagnostic] = []
    for setting, slot, code, label in (
        ("mesh_file", "meshes", "entity.missing_mesh_asset", "mesh"),
        ("animation_file", "animations", "entity.missing_animation_asset", "animation"),
    ):
        expected = settings_map.get(setting)
        if isinstance(expected, str) and expected in bundle.source_slots.get(slot, ()):
            diagnostics.extend(
                _binary_asset_diagnostics(
                    module,
                    bundle,
                    path=expected,
                    slot=slot,
                    label=label,
                )
            )
            continue
        expected_path = expected if isinstance(expected, str) and expected else f"settings.{setting}"
        diagnostics.append(
            Diagnostic(
                code=code,
                message=(
                    f"Entity module {module.module_id} must attach its referenced {label} binary at "
                    f"{expected_path!r}. Use the entity Assets tab before building."
                ),
                severity="error",
                family=EntityFamily.family,
                module_id=module.module_id,
                slot=slot,
                source_path=str(expected_path),
            )
        )
    diagnostics.extend(_starter_definition_diagnostics(module, bundle, settings_map))
    return tuple(diagnostics)


def _is_starter_module(
    settings: Mapping[object, object],
) -> bool:
    if settings.get("authoring_contract") == _AUTHORING_CONTRACT:
        return True
    return "mesh_file" in settings or "animation_file" in settings


def _binary_asset_diagnostics(
    module: Module,
    bundle: ModuleSourceBundle,
    *,
    path: str,
    slot: str,
    label: str,
) -> tuple[Diagnostic, ...]:
    try:
        content = load_bin(pj(bundle.root, path), strict=True)
    except OSError:
        content = b""
    if _complete_pdxasseti(content, label=label):
        return ()
    return (
        Diagnostic(
            code=f"entity.invalid_{label}_asset",
            message=(
                f"Entity module {module.module_id} {label} asset {path!r} does not contain the required "
                "Paradox pdxasseti v2 structure. Export the file again before building."
            ),
            severity="error",
            family=EntityFamily.family,
            module_id=module.module_id,
            slot=slot,
            source_path=path,
        ),
    )


def _complete_pdxasseti(content: bytes, *, label: str) -> bool:
    markers = _PDXASSETI_MARKERS.get(label)
    if markers is None or not content.startswith(_PDXASSETI_V2_HEADER):
        return False
    cursor = len(_PDXASSETI_V2_HEADER)
    for index, marker in enumerate(markers):
        position = content.find(marker, cursor)
        if position < cursor or (index == 0 and position != cursor):
            return False
        cursor = position + len(marker)
    return True


def _starter_definition_diagnostics(
    module: Module,
    bundle: ModuleSourceBundle,
    settings: Mapping[object, object],
) -> tuple[Diagnostic, ...]:
    object_id = module.module_id.rsplit("/", 1)[-1]
    prefix = f"gfx/models/{object_id}/"
    expected_sources = {
        "mesh": f"{prefix}mesh.gfx",
        "entity": f"{prefix}entity.asset",
        "animation": f"{prefix}animations.asset",
    }
    sources = {source.path: source.block for source in bundle.pdx_sources}
    diagnostics: list[Diagnostic] = []
    for path in expected_sources.values():
        if path in sources:
            continue
        diagnostics.append(
            Diagnostic(
                code="entity.missing_starter_definition",
                message=f"Entity module {module.module_id} must keep its starter definition {path!r}.",
                severity="error",
                family=EntityFamily.family,
                module_id=module.module_id,
                slot="pdx",
                source_path=path,
            )
        )
    if diagnostics:
        return tuple(diagnostics)

    mesh_path = expected_sources["mesh"]
    entity_path = expected_sources["entity"]
    animation_path = expected_sources["animation"]
    mesh = _nested_block(_nested_block(sources[mesh_path], "objectTypes"), "pdxmesh")
    mesh_animation = _nested_block(mesh, "animation")
    entity = _nested_block(sources[entity_path], "entity")
    entity_state = _nested_block(entity, "state")
    animation = _nested_block(sources[animation_path], "animation")
    expected_mesh_file = settings.get("mesh_file")
    expected_animation_file = settings.get("animation_file")
    expected_animation_path = expected_animation_file.replace("\\", "/") if isinstance(expected_animation_file, str) else None
    expected_animation_parent, _, expected_animation_name = (expected_animation_path or "").rpartition("/")

    if not isinstance(expected_mesh_file, str) or _scalar_text(mesh, "file") != expected_mesh_file:
        diagnostics.append(
            _definition_diagnostic(
                module,
                code="entity.invalid_mesh_reference",
                message=f"{mesh_path!r} must reference settings.mesh_file exactly.",
                source_path=mesh_path,
            )
        )
    animation_reference = _scalar_text(animation, "file")
    if expected_animation_path is None or expected_animation_parent != animation_path.rpartition("/")[0] or animation_reference != expected_animation_name:
        diagnostics.append(
            _definition_diagnostic(
                module,
                code="entity.invalid_animation_reference",
                message=(
                    f"{animation_path!r} must reference the filename from settings.animation_file, "
                    "and that binary must be stored beside the animation definition."
                ),
                source_path=animation_path,
            )
        )

    mesh_name = _scalar_text(mesh, "name")
    mesh_animation_id = _scalar_text(mesh_animation, "id")
    mesh_animation_type = _scalar_text(mesh_animation, "type")
    state_name = _scalar_text(entity_state, "name")
    state_animation = _scalar_text(entity_state, "animation")
    links = (
        mesh_name,
        _scalar_text(entity, "pdxmesh"),
        mesh_animation_id,
        _scalar_text(entity, "default_state"),
        state_name,
        state_animation,
        mesh_animation_type,
        _scalar_text(animation, "name"),
    )
    if (
        not mesh_name
        or links[1] != mesh_name
        or not mesh_animation_id
        or links[3] != mesh_animation_id
        or state_name != mesh_animation_id
        or state_animation != mesh_animation_id
        or not mesh_animation_type
        or links[7] != mesh_animation_type
    ):
        diagnostics.append(
            _definition_diagnostic(
                module,
                code="entity.invalid_definition_links",
                message=("Starter mesh, entity state, and animation declarations must reference the same " "mesh name, state id, and animation type."),
                source_path=entity_path,
            )
        )
    return tuple(diagnostics)


def _nested_block(block: PDXBlock | None, key: str) -> PDXBlock | None:
    if block is None:
        return None
    entry = block.find(key)
    return entry.val if entry is not None and isinstance(entry.val, PDXBlock) else None


def _scalar_text(block: PDXBlock | None, key: str) -> str | None:
    if block is None:
        return None
    entry = block.find(key)
    return str(entry.val.val) if entry is not None and isinstance(entry.val, PDXScalar) else None


def _definition_diagnostic(
    module: Module,
    *,
    code: str,
    message: str,
    source_path: str,
) -> Diagnostic:
    return Diagnostic(
        code=code,
        message=f"Entity module {module.module_id} {message}",
        severity="error",
        family=EntityFamily.family,
        module_id=module.module_id,
        slot="pdx",
        source_path=source_path,
    )


def _module_bundle(module: Module) -> ModuleSourceBundle:
    if isinstance(module.payload, ModuleSourceBundle):
        return module.payload
    raise ValueError(f"Module {module.module_id!r} must carry a ModuleSourceBundle payload.")
