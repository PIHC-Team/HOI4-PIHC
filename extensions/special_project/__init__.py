"""PIHC3 special project Entity and compiler."""

from __future__ import annotations

import heavenbase as hb

from paradev.build import (
    Artifact,
    BuildContext,
    Collection,
    Diagnostic,
    Module,
    SimpleSourceFamily,
    Slot,
)


class PIHC3SpecialProjectModule(hb.Entity):
    """One independently editable special project or shared resource set."""

    identifier = "pihc3-special-project-module"
    module_id = (
        hb.field(hb.ShortText).default("").desc("Stable ParaDev module identifier.")
    )
    data = (
        hb.field(hb.Json)
        .default({})
        .desc("Structured metadata, localization, and resource references.")
    )
    family = "special_project"
    resource_slots = (
        Slot(
            name="def",
            match="def.txt",
            kind="pdx",
        ),
        Slot(
            name="loc",
            match="**/*.loc",
            many=True,
            kind="loc",
        ),
        Slot(
            name="icon",
            match="^icon\\.(png|dds|tga)$",
            regex=True,
            kind="copy",
            authoring_path="{filename}",
        ),
        Slot(
            name="shared_pdx",
            match=(
                "^common/special_projects/"
                "(project_tags|projects|specialization)/.*\\.txt$"
            ),
            many=True,
            regex=True,
            kind="pdx",
        ),
        Slot(
            name="shared_assets",
            match="^gfx/interface/special_project/[^/]+\\.dds$",
            many=True,
            regex=True,
            kind="copy",
            authoring_path="gfx/interface/special_project/{filename}",
        ),
        Slot(
            name="shared_assets",
            match="^interface/PIHC_special_projects\\.gfx$",
            many=True,
            regex=True,
            kind="copy",
            authoring_path="interface/{filename}",
        ),
        Slot(
            name="shared_assets",
            match="^interface/special_projects/.*\\.gui$",
            many=True,
            regex=True,
            kind="copy",
            authoring_path="interface/special_projects/{filename}",
        ),
    )
    compilation_hooks = ("normalize", "check", "emit")


class PIHC3SpecialProjectFamily(SimpleSourceFamily):
    """Compile special-project nodes and their shared supporting resources."""

    replaces_registered_family = True

    def __init__(self) -> None:
        super().__init__(
            family=PIHC3SpecialProjectModule.family,
            pdx_path_template=("common/special_projects/projects/{object_id}.txt"),
            loc_path_template=(
                "localisation/{language_folder}/{object_id}_{language}.yml"
            ),
            copy_path_template=(
                "gfx/interface/special_project/project_icons/{object_id}{source_suffix}"
            ),
            sprite_gfx_path_template=("interface/special_projects/{object_id}.gfx"),
            sprite_name_template="GFX_{object_id}",
            sprite_slots=("icon",),
            source_slots=PIHC3SpecialProjectModule.resource_slots,
            required_loc_keys=("{object_id}", "{object_id}_desc"),
        )

    def check(
        self,
        ctx: BuildContext,
        modules: tuple[Module, ...],
        collections: tuple[Collection, ...],
    ) -> tuple[Diagnostic, ...]:
        """Validate authored project nodes without imposing node fields on support."""

        authored = tuple(module for module in modules if module.source_slots.get("def"))
        return super().check(ctx, authored, collections)

    def emit(
        self,
        ctx: BuildContext,
        modules: tuple[Module, ...],
        collections: tuple[Collection, ...],
    ) -> tuple[Artifact, ...]:
        """Emit authored projects and source-path-preserving shared resources."""

        shared = tuple(
            module
            for module in modules
            if module.source_slots.get("shared_pdx")
            or module.source_slots.get("shared_assets")
        )
        owned = tuple(
            module
            for module in modules
            if not module.source_slots.get("shared_pdx")
            and not module.source_slots.get("shared_assets")
        )
        shared_family = SimpleSourceFamily(
            family=self.family,
            pdx_path_template="{source_path}",
            copy_path_template="{source_path}",
            source_slots=self.source_slots,
        )
        return (
            *super().emit(ctx, owned, collections),
            *shared_family.emit(ctx, shared, ()),
        )


def build_family() -> PIHC3SpecialProjectFamily:
    """HeavenBase Registry target for the PIHC3 special-project compiler."""

    return PIHC3SpecialProjectFamily()


__all__ = [
    "PIHC3SpecialProjectFamily",
    "PIHC3SpecialProjectModule",
    "build_family",
]
