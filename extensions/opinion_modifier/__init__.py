"""PIHC3 compiler overlay for the built-in opinion-modifier family."""

from __future__ import annotations

from paradev.build import FamilyPresentation, SimpleSourceFamily, Slot

OPINION_MODIFIER_RESOURCE_SLOTS = (
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


class PIHC3OpinionModifierFamily(SimpleSourceFamily):
    """Compile PIHC3 opinion modifiers with project-owned source slots."""

    replaces_registered_family = True

    def __init__(self) -> None:
        super().__init__(
            family="opinion_modifier",
            presentation=FamilyPresentation(
                id="opinion-modifiers",
                title="Opinion Modifiers",
                group="country",
                title_key="modules.opinionModifiers.title",
            ),
            pdx_path_template="common/opinion_modifiers/{object_id}.txt",
            loc_path_template=("localisation/{language_folder}/{object_id}_{language}.yml"),
            copy_path_template="gfx/paradev/{object_id}/{source_path}",
            source_slots=OPINION_MODIFIER_RESOURCE_SLOTS,
        )


def build_family() -> PIHC3OpinionModifierFamily:
    """Return the PIHC3 overlay for the built-in opinion-modifier family."""

    return PIHC3OpinionModifierFamily()


__all__ = [
    "PIHC3OpinionModifierFamily",
    "build_family",
]
