"""PIHC3 state-lore Entity and aggregate compiler."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import ClassVar

import heavenbase as hb
from heavenbase.utils import pj

from paradev.build import (
    Artifact,
    BuildContext,
    BuildRegistry,
    Collection,
    Diagnostic,
    Module,
    ModuleSourceBundle,
    SimpleSourceFamily,
    Slot,
)
from paradev.pdx import PDXBlock, PDXEntry, PDXScalar

STATE_LORE_ENTITY_ID = "pihc3-state-lore"
STATE_LORE_FAMILY = "state_lore"
STATE_LORE_VARIANTS_PATH = "variants.pdx"
STATE_LORE_SOURCE_SLOTS = (
    Slot(
        name="variants",
        match=STATE_LORE_VARIANTS_PATH,
        kind="pdx",
    ),
    Slot(
        name="loc",
        match="**/*.loc",
        kind="loc",
        many=True,
        required=True,
    ),
)

_SOURCE_FORM_FIELD_HINTS = {
    "variant": {
        "label": {"default": "Conditional lore variant", "zh": "条件传说文本"},
        "description": {
            "default": "Optional text shown before the default lore when its trigger passes.",
            "zh": "触发条件满足时，优先于默认传说显示的可选文本。",
        },
    },
    "localization_key": {
        "label": {"default": "Localization key", "zh": "本地化键"},
        "description": {
            "default": "Module-owned localization key for this conditional text.",
            "zh": "此条件文本在当前模块中拥有的本地化键。",
        },
    },
    "trigger": {
        "label": {"default": "Trigger", "zh": "触发条件"},
        "description": {
            "default": "HoI4 trigger body for this conditional lore variant.",
            "zh": "此条件传说变体使用的 HoI4 触发器内容。",
        },
        "control": "block-text",
    },
}


class StateLore(hb.Entity):
    """PIHC3 state lore with compact localization and optional variants."""

    identifier = STATE_LORE_ENTITY_ID

    state_id = hb.field(hb.Integer).desc("Positive HoI4 state id derived from STATE_LORE_<state id>.")
    title = hb.field(hb.ShortText).default("").desc("Display title shared with the matching State module.")
    description = hb.field(hb.LongText).default("").desc("Preferred-language lore text.")
    variants = hb.field(hb.Json).default([]).desc("Optional conditional localization keys and HoI4 trigger bodies.")
    localization = hb.field(hb.Json).default({}).desc("Localized state-lore text.")

    family = STATE_LORE_FAMILY
    resource_slots = STATE_LORE_SOURCE_SLOTS
    compilation_hooks = ("normalize", "check", "emit")
    source_form_field_hints = _SOURCE_FORM_FIELD_HINTS

    @classmethod
    def build_family(cls) -> PIHC3StateLoreFamily:
        """Return the aggregate compiler declared by this Entity type.

        Args:
            None.

        Returns:
            PIHC3StateLoreFamily: Project-owned state-lore compiler.
        """

        return PIHC3StateLoreFamily()


class PIHC3StateLoreFamily:
    """Generate PIHC3 state-lore aggregates from compact module sources."""

    family_kind: ClassVar[str] = "state_lore_aggregate"
    family: ClassVar[str] = STATE_LORE_FAMILY
    scripted_localisation_path: ClassVar[str] = "common/scripted_localisation/PIHC_STATE_LORES.txt"
    on_actions_path: ClassVar[str] = "common/on_actions/PIHC_STATE_LORES.txt"
    loc_path_template: ClassVar[str] = "localisation/{language_folder}/{object_id}_{language}.yml"
    source_slots: ClassVar[tuple[Slot, ...]] = STATE_LORE_SOURCE_SLOTS
    metadata_keys: ClassVar[tuple[str, ...]] = ()
    settings_keys: ClassVar[tuple[str, ...]] = ()
    settings_values: ClassVar[Mapping[str, tuple[str, ...]]] = {}
    required_settings: ClassVar[tuple[str, ...]] = ()
    required_loc_keys: ClassVar[tuple[str, ...]] = ("{object_id}",)
    title_loc_keys: ClassVar[tuple[str, ...]] = ()
    asset_constraints: ClassVar[Mapping[str, Mapping[str, object]]] = {}
    settings_normalizers: ClassVar[Mapping[str, object]] = {}
    source_form_field_hints: ClassVar[Mapping[str, Mapping[str, object]]] = _SOURCE_FORM_FIELD_HINTS
    generated_outputs: ClassVar[tuple[Mapping[str, object], ...]] = (
        {
            "artifact_type": "pdx",
            "owner_kinds": ("project",),
            "target_root": "output",
        },
        {
            "artifact_type": "loc",
            "owner_kinds": ("module",),
            "target_root": "output",
        },
    )

    def validate_source_text(
        self,
        *,
        module_id: str,
        relative_path: str,
        text: str,
    ) -> None:
        """Reject malformed conditional variants before a draft write.

        Args:
            module_id (str): Canonical `state_lore/<object id>` identity.
            relative_path (str): Module-relative source path.
            text (str): Proposed UTF-8 source text.

        Returns:
            None: This function does not return a value.

        Raises:
            ValueError: If `variants.pdx` violates the compact source contract.
        """

        if relative_path != STATE_LORE_VARIANTS_PATH:
            return
        object_id = module_id.rsplit("/", 1)[-1]
        _variants_from_block(
            PDXBlock.from_str(text),
            object_id=object_id,
            label=f"{module_id}/{relative_path}",
        )

    def check(
        self,
        ctx: BuildContext,
        modules: tuple[Module, ...],
        collections: tuple[Collection, ...],
    ) -> tuple[Diagnostic, ...]:
        """Validate state identities, variants, and module-owned localization.

        Args:
            ctx (BuildContext): Active project build context.
            modules (tuple[Module, ...]): Selected state-lore modules.
            collections (tuple[Collection, ...]): Selected collections.

        Returns:
            tuple[Diagnostic, ...]: Stable diagnostics for invalid sources.
        """

        diagnostics = list(_loc_family().check(ctx, modules, collections))
        for module in modules:
            state_id = _module_state_id(module)
            if state_id is None:
                diagnostics.append(
                    Diagnostic(
                        code="state_lore.invalid_object_id",
                        message=(f"State lore module {module.module_id!r} must use " "STATE_LORE_<positive state id>."),
                        severity="error",
                        family=self.family,
                        module_id=module.module_id,
                    )
                )
            try:
                variants = _module_variants(module)
            except ValueError as error:
                diagnostics.append(
                    Diagnostic(
                        code="state_lore.invalid_variants",
                        message=str(error),
                        severity="error",
                        family=self.family,
                        module_id=module.module_id,
                        slot="variants",
                        source_path=STATE_LORE_VARIANTS_PATH,
                    )
                )
                continue
            diagnostics.extend(_variant_localization_diagnostics(module, variants))
        return tuple(diagnostics)

    def emit(
        self,
        ctx: BuildContext,
        modules: tuple[Module, ...],
        collections: tuple[Collection, ...],
    ) -> tuple[Artifact, ...]:
        """Emit localization and the two project-owned aggregate files.

        Args:
            ctx (BuildContext): Active project build context.
            modules (tuple[Module, ...]): Selected state-lore modules.
            collections (tuple[Collection, ...]): Selected collections.

        Returns:
            tuple[Artifact, ...]: Module localization and aggregate PDX artifacts.
        """

        ordered = tuple(sorted(modules, key=_module_sort_key))
        artifacts: list[Artifact] = list(_loc_family().emit(ctx, ordered, collections))
        scripted = _scripted_localisation_artifact(ctx, ordered)
        if scripted is not None:
            artifacts.append(scripted)
        on_actions = _on_actions_artifact(ctx, ordered)
        if on_actions is not None:
            artifacts.append(on_actions)
        return tuple(artifacts)


def register(registry: BuildRegistry) -> BuildRegistry:
    """Register the project-owned state-lore family.

    Args:
        registry (BuildRegistry): Project build-family Registry.

    Returns:
        BuildRegistry: The same Registry with state lore registered.
    """

    return registry.add(PIHC3StateLoreFamily())


def _loc_family() -> SimpleSourceFamily:
    return SimpleSourceFamily(
        family=STATE_LORE_FAMILY,
        loc_path_template=PIHC3StateLoreFamily.loc_path_template,
        source_slots=STATE_LORE_SOURCE_SLOTS,
        required_loc_keys=PIHC3StateLoreFamily.required_loc_keys,
        title_loc_keys=(),
    )


def _scripted_localisation_artifact(
    ctx: BuildContext,
    modules: tuple[Module, ...],
) -> Artifact | None:
    name_texts: list[PDXEntry] = []
    desc_texts: list[PDXEntry] = []
    inputs: list[str] = []

    for module in modules:
        state_id = _module_state_id(module)
        if state_id is None:
            continue
        object_id = _module_object_id(module)
        bundle = _module_bundle(module)
        inputs.extend(_module_input_paths(bundle))
        name_texts.append(
            _state_lore_text_entry(
                _state_trigger_block(state_id),
                f"[{state_id}.GetName]",
            )
        )
        variants = _module_variants(module)
        desc_texts.extend(
            _state_lore_text_entry(
                _state_trigger_block(state_id, extra_entries=trigger.entries),
                localization_key,
            )
            for localization_key, trigger in variants
        )
        desc_texts.append(_state_lore_text_entry(_state_trigger_block(state_id), object_id))

    entries: list[PDXEntry] = []
    if name_texts:
        entries.append(_defined_text_entry("GetCurentStateLoreName", name_texts))
    if desc_texts:
        entries.append(_defined_text_entry("GetCurentStateLoreDesc", desc_texts))
    if not entries:
        return None
    return Artifact(
        path=PIHC3StateLoreFamily.scripted_localisation_path,
        artifact_type="pdx",
        owner=f"project:{ctx.project_id}",
        inputs=tuple(inputs),
        metadata={
            "family": STATE_LORE_FAMILY,
            "source_slot": "variants",
            "module_count": len(modules),
            "name_text_count": len(name_texts),
            "description_text_count": len(desc_texts),
        },
        payload=PDXBlock.from_entries(entries),
    )


def _on_actions_artifact(
    ctx: BuildContext,
    modules: tuple[Module, ...],
) -> Artifact | None:
    add_entries: list[PDXEntry] = []
    inputs: list[str] = []

    for module in modules:
        state_id = _module_state_id(module)
        if state_id is None:
            continue
        add_entries.append(_state_lore_add_to_array_entry(state_id))
        inputs.extend(_module_input_paths(_module_bundle(module)))

    if not add_entries:
        return None
    block = PDXBlock.from_entries(
        [
            PDXEntry.kv(
                "on_actions",
                PDXBlock.from_entries(
                    [
                        PDXEntry.kv(
                            "on_startup",
                            PDXBlock.from_entries(
                                [
                                    PDXEntry.kv(
                                        "effect",
                                        PDXBlock.from_entries(
                                            [
                                                PDXEntry.kv_id(
                                                    "clear_array",
                                                    "global.states_with_lore",
                                                ),
                                                *(entry.clone() for entry in add_entries),
                                            ]
                                        ),
                                    )
                                ]
                            ),
                        )
                    ]
                ),
            )
        ]
    )
    return Artifact(
        path=PIHC3StateLoreFamily.on_actions_path,
        artifact_type="pdx",
        owner=f"project:{ctx.project_id}",
        inputs=tuple(inputs),
        metadata={
            "family": STATE_LORE_FAMILY,
            "source_slot": "variants",
            "module_count": len(modules),
            "state_count": len(add_entries),
        },
        payload=block,
    )


def _module_variants(module: Module) -> tuple[tuple[str, PDXBlock], ...]:
    bundle = _module_bundle(module)
    sources = tuple(source for source in bundle.pdx_sources if source.slot == "variants")
    if not sources:
        return ()
    if len(sources) != 1:
        raise ValueError(f"State lore {module.module_id!r} must own at most one " f"{STATE_LORE_VARIANTS_PATH}.")
    source = sources[0]
    return _variants_from_block(
        source.block,
        object_id=_module_object_id(module),
        label=f"{module.module_id}/{source.path}",
    )


def _variants_from_block(
    block: PDXBlock,
    *,
    object_id: str,
    label: str,
) -> tuple[tuple[str, PDXBlock], ...]:
    if not block.entries:
        raise ValueError(f"{label} is empty; remove the optional file instead.")
    variants: list[tuple[str, PDXBlock]] = []
    keys: set[str] = set()
    for index, entry in enumerate(block.entries, start=1):
        if entry.key_str != "variant" or entry.op != "=" or not isinstance(entry.val, PDXBlock):
            raise ValueError(f"{label} entry {index} must be a variant = {{ ... }} block.")
        fields = entry.val.entries
        if len(fields) != 2:
            raise ValueError(f"{label} variant {index} must contain exactly one localization_key and one trigger.")
        unknown = sorted({str(field.key_str) for field in fields if field.key_str not in {"localization_key", "trigger"}})
        if unknown:
            raise ValueError(f"{label} variant {index} has unsupported fields: {', '.join(unknown)}.")
        localization_keys = [
            str(field.val.val) for field in fields if field.key_str == "localization_key" and field.op == "=" and isinstance(field.val, PDXScalar)
        ]
        triggers = [field.val for field in fields if field.key_str == "trigger" and field.op == "=" and isinstance(field.val, PDXBlock)]
        if len(localization_keys) != 1 or not localization_keys[0].strip():
            raise ValueError(f"{label} variant {index} must contain exactly one non-empty localization_key.")
        localization_key = localization_keys[0].strip()
        if localization_key == object_id or not localization_key.startswith(f"{object_id}_"):
            raise ValueError(f"{label} variant {index} localization_key must start with " f"{object_id!r} plus an underscore.")
        if localization_key in keys:
            raise ValueError(f"{label} repeats localization_key {localization_key!r}.")
        if len(triggers) != 1 or not triggers[0].entries:
            raise ValueError(f"{label} variant {index} must contain exactly one non-empty trigger block.")
        if _contains_key(triggers[0], "check_variable"):
            raise ValueError(f"{label} variant {index} must not author compiler-owned " "check_variable state routing.")
        keys.add(localization_key)
        variants.append((localization_key, triggers[0].clone()))
    return tuple(variants)


def _variant_localization_diagnostics(
    module: Module,
    variants: tuple[tuple[str, PDXBlock], ...],
) -> tuple[Diagnostic, ...]:
    if not variants:
        return ()
    bundle = _module_bundle(module)
    localized = {(entry.language, entry.key) for entry in bundle.loc_entries}
    object_id = _module_object_id(module)
    languages = sorted({entry.language for entry in bundle.loc_entries if entry.key == object_id})
    localization_paths = sorted({entry.source_path for entry in bundle.loc_entries if entry.key == object_id})
    diagnostics: list[Diagnostic] = []
    for localization_key, _trigger in variants:
        missing = [language for language in languages if (language, localization_key) not in localized]
        if not missing:
            continue
        diagnostics.append(
            Diagnostic(
                code="state_lore.missing_variant_localization",
                message=(f"State lore {module.module_id!r} localization key " f"{localization_key!r} is missing languages: {', '.join(missing)}."),
                severity="error",
                family=STATE_LORE_FAMILY,
                module_id=module.module_id,
                slot="loc",
                source_path=localization_paths[0] if len(localization_paths) == 1 else None,
            )
        )
    return tuple(diagnostics)


def _contains_key(block: PDXBlock, key: str) -> bool:
    for entry in block.entries:
        if entry.key_str == key:
            return True
        if isinstance(entry.val, PDXBlock) and _contains_key(entry.val, key):
            return True
    return False


def _module_input_paths(bundle: ModuleSourceBundle) -> tuple[str, ...]:
    paths = {source.path for source in bundle.pdx_sources if source.slot == "variants"}
    paths.update(entry.source_path for entry in bundle.loc_entries)
    return tuple(pj(bundle.root, path) for path in sorted(paths))


def _state_trigger_block(
    state_id: int,
    *,
    extra_entries: Sequence[PDXEntry] = (),
) -> PDXBlock:
    return PDXBlock.from_entries(
        [
            PDXEntry.kv(
                "check_variable",
                PDXBlock.from_entries(
                    [
                        PDXEntry.kv_id(
                            "state_lore_text_state_id",
                            f"{state_id}.id",
                        )
                    ]
                ),
            ),
            *(entry.clone() for entry in extra_entries),
        ]
    )


def _state_lore_text_entry(trigger: PDXBlock, localization_key: str) -> PDXEntry:
    return PDXEntry.kv(
        "text",
        PDXBlock.from_entries(
            [
                PDXEntry.kv("trigger", trigger),
                PDXEntry.kv_id("localization_key", localization_key),
            ]
        ),
    )


def _state_lore_add_to_array_entry(state_id: int) -> PDXEntry:
    return PDXEntry.kv(
        "add_to_array",
        PDXBlock.from_entries([PDXEntry.kv_id("global.states_with_lore", f"{state_id}.id")]),
    )


def _defined_text_entry(name: str, text_entries: Sequence[PDXEntry]) -> PDXEntry:
    return PDXEntry.kv(
        "defined_text",
        PDXBlock.from_entries(
            [
                PDXEntry.kv_id("name", name),
                *(entry.clone() for entry in text_entries),
            ]
        ),
    )


def _module_bundle(module: Module) -> ModuleSourceBundle:
    if isinstance(module.payload, ModuleSourceBundle):
        return module.payload
    raise ValueError(f"State lore module {module.module_id!r} must carry a " "ModuleSourceBundle payload.")


def _module_state_id(module: Module) -> int | None:
    object_id = _module_object_id(module)
    prefix = "STATE_LORE_"
    suffix = object_id[len(prefix) :] if object_id.startswith(prefix) else ""
    if not suffix.isdigit():
        return None
    state_id = int(suffix)
    return state_id if state_id > 0 else None


def _module_object_id(module: Module) -> str:
    value = module.metadata.get("object_id")
    if isinstance(value, str) and value:
        return value
    return module.module_id.rsplit("/", 1)[-1]


def _module_sort_key(module: Module) -> tuple[str, int, str]:
    state_id = _module_state_id(module)
    return (str(state_id or ""), state_id or 0, module.module_id)


__all__ = [
    "STATE_LORE_ENTITY_ID",
    "STATE_LORE_FAMILY",
    "STATE_LORE_SOURCE_SLOTS",
    "STATE_LORE_VARIANTS_PATH",
    "PIHC3StateLoreFamily",
    "StateLore",
    "register",
]
