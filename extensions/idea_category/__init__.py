"""PIHC3 idea-category Entity and compiler."""

from __future__ import annotations

import heavenbase as hb

from paradev.build import SimpleSourceFamily, Slot


class PIHC3IdeaCategory(hb.Entity):
    """One PIHC3 idea category and its category-scoped ideas."""

    identifier = "pihc3-idea-category"
    title = hb.field(hb.ShortText).default("")
    family = "idea_category"
    resource_slots = (
        Slot("def", "def.txt", required=True, kind="pdx"),
        Slot("loc", "**/*.loc", many=True, kind="loc"),
        Slot("preview", "preview.png"),
        Slot(
            "compiled_assets",
            r"^gfx/interface/ideas/.*\.dds$",
            many=True,
            regex=True,
            kind="copy",
            authoring_path="gfx/interface/ideas/{filename}",
        ),
        Slot(
            "compiled_assets",
            r"^interface/ideas/.*\.gfx$",
            many=True,
            regex=True,
            kind="copy",
            authoring_path="interface/ideas/{filename}",
        ),
    )
    compilation_hooks = ("normalize", "check", "emit")

    @classmethod
    def build_family(cls) -> "PIHC3IdeaCategoryFamily":
        """Return the project-owned idea-category compiler."""

        return PIHC3IdeaCategoryFamily()


class PIHC3IdeaCategoryFamily(SimpleSourceFamily):
    """Compile idea categories together with their category-owned icons."""

    replaces_registered_family = True

    def __init__(self) -> None:
        super().__init__(
            family=PIHC3IdeaCategory.family,
            pdx_path_template="common/ideas/{object_id}.txt",
            loc_path_template=(
                "localisation/{language_folder}/{object_id}_{language}.yml"
            ),
            copy_path_template="{source_path}",
            source_slots=PIHC3IdeaCategory.resource_slots,
            required_loc_keys=(
                "{object_id}",
                "{object_id}_desc",
                "{object_id}__cost_factor",
            ),
        )


def build_family() -> PIHC3IdeaCategoryFamily:
    """HeavenBase Registry target for the PIHC3 idea-category compiler."""

    return PIHC3IdeaCategory.build_family()
