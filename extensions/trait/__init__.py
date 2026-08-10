"""PIHC3 compiler overlay for the built-in trait family."""

from __future__ import annotations

from paradev.build import (
    FamilyPresentation,
    RoutedSourceFamily,
    Slot,
    SourceRoute,
)

TRAIT_RESOURCE_SLOTS = (
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
        match="^(icon|goal|portrait|picture)\\.(png|dds|tga)$",
        regex=True,
        kind="copy",
        authoring_path="{filename}",
    ),
    Slot(
        name="copy",
        match="copy/*",
        many=True,
        kind="copy",
        authoring_path="copy/{filename}",
    ),
    Slot(
        name="assets",
        match="assets/*",
        many=True,
        kind="copy",
        authoring_path="assets/{filename}",
    ),
)


class PIHC3TraitFamily(RoutedSourceFamily):
    """Compile each PIHC3 trait subtype through its project-owned route."""

    replaces_registered_family = True

    def __init__(self) -> None:
        super().__init__(
            family="trait",
            presentation=FamilyPresentation(
                id="traits",
                title="Traits",
                group="country",
                title_key="modules.traits.title",
            ),
            routes={
                "country_leader": SourceRoute(
                    pdx_path_template="common/country_leader/{object_id}.txt",
                    loc_path_template=("localisation/{language_folder}/{object_id}_{language}.yml"),
                    copy_path_template="gfx/paradev/{object_id}/{source_path}",
                ),
                "scientist": SourceRoute(
                    pdx_path_template="common/scientist_traits/{object_id}.txt",
                    loc_path_template=("localisation/{language_folder}/{object_id}_{language}.yml"),
                    copy_path_template="gfx/paradev/{object_id}/{source_path}",
                ),
                "unit_leader": SourceRoute(
                    pdx_path_template="common/unit_leader/{object_id}.txt",
                    loc_path_template=("localisation/{language_folder}/{object_id}_{language}.yml"),
                    copy_path_template="gfx/paradev/{object_id}/{source_path}",
                ),
            },
            default_route="country_leader",
            source_slots=TRAIT_RESOURCE_SLOTS,
        )


def build_family() -> PIHC3TraitFamily:
    """Return the PIHC3 overlay for the built-in trait family."""

    return PIHC3TraitFamily()


__all__ = ["PIHC3TraitFamily", "build_family"]
