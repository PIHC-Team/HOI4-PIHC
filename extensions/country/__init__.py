"""PIHC3 country Entity and compiler."""

from __future__ import annotations

from io import BytesIO
from typing import ClassVar

import heavenbase as hb
from heavenbase.utils import pj, save_bin
from PIL import Image

from paradev.build import Artifact, BuildContext, Collection, Module, SimpleSourceFamily, Slot, content_sha256

FLAG_ARTIFACT_TYPE = "pihc3_country_flag"
FLAG_VARIANT_SIZES = {
    "medium": (41, 26),
    "small": (10, 7),
}


class PIHC3Country(hb.Entity):
    """One PIHC3 country definition with its full flag set."""

    identifier = "pihc3-country"
    title = hb.field(hb.ShortText).default("")
    family = "country"
    resource_slots = (
        Slot("def", "def.txt", required=True, kind="pdx"),
        Slot("loc", "**/*.loc", many=True, kind="loc"),
        Slot("preview", "preview.png"),
        Slot(
            "flags",
            r"^gfx/flags/.*\.tga$",
            many=True,
            regex=True,
            kind="copy",
            authoring_path="gfx/flags/{filename}",
        ),
    )
    compilation_hooks = ("normalize", "check", "emit")
    # HeavenBase Entity annotations are logical fields; protocol metadata stays unannotated.
    source_form_field_hints = {  # noqa: RUF012
        "graphical_culture": {
            "description": {
                "default": "3D graphical-culture identifier used by this country.",
                "zh": "该国家使用的 3D 图形文化标识。",
            }
        },
        "graphical_culture_2d": {
            "description": {
                "default": "2D graphical-culture identifier used by this country's interface art.",
                "zh": "该国家界面美术使用的 2D 图形文化标识。",
            }
        },
    }

    @classmethod
    def build_family(cls) -> "PIHC3CountryFamily":
        """Return the project-owned country compiler."""

        return PIHC3CountryFamily()


class PIHC3CountryFamily(SimpleSourceFamily):
    """Compile country definitions together with their country-owned flags."""

    replaces_registered_family = True
    source_form_field_hints: ClassVar[dict[str, dict[str, object]]] = PIHC3Country.source_form_field_hints

    def __init__(self) -> None:
        super().__init__(
            family=PIHC3Country.family,
            pdx_path_template="common/countries/{object_id}.txt",
            loc_path_template=("localisation/{language_folder}/{object_id}_{language}.yml"),
            copy_path_template="{source_path}",
            source_slots=PIHC3Country.resource_slots,
            required_loc_keys=("{object_id}", "{object_id}_DESC"),
            title_loc_keys=("{object_id}_DEF", "{object_id}"),
        )

    def emit(
        self,
        ctx: BuildContext,
        modules: tuple[Module, ...],
        collections: tuple[Collection, ...],
    ) -> tuple[Artifact, ...]:
        """Emit authored country resources and absent scaled flag variants."""

        artifacts = tuple(super().emit(ctx, modules, collections))
        existing_paths = {_artifact_path(artifact) for artifact in artifacts}
        generated: list[Artifact] = []
        for artifact in artifacts:
            source_path = _artifact_path(artifact)
            if artifact.artifact_type != "copy" or not _is_full_flag_path(source_path):
                continue
            if len(artifact.inputs) != 1:
                raise ValueError(f"PIHC3 country flag {source_path!r} must have exactly one source input.")
            filename = source_path.rsplit("/", 1)[-1]
            for variant, size in FLAG_VARIANT_SIZES.items():
                target_path = f"gfx/flags/{variant}/{filename}"
                if target_path in existing_paths:
                    continue
                existing_paths.add(target_path)
                generated.append(
                    Artifact(
                        path=target_path,
                        artifact_type=FLAG_ARTIFACT_TYPE,
                        owner=artifact.owner,
                        inputs=artifact.inputs,
                        metadata={
                            "generated_from": source_path,
                            "height": size[1],
                            "width": size[0],
                        },
                        payload=_scaled_flag_bytes(str(artifact.inputs[0]), size),
                    )
                )
        return (*artifacts, *generated)


class PIHC3CountryFlagWriter:
    """Write one deterministic scaled PIHC3 country flag."""

    artifact_type = FLAG_ARTIFACT_TYPE

    def expected_sha256(self, artifact: Artifact) -> str:
        """Return the exact digest of the prepared flag payload."""

        return content_sha256(self.render_bytes(artifact))

    def render_bytes(self, artifact: Artifact) -> bytes:
        """Return the prepared TGA bytes for direct publication."""

        if not isinstance(artifact.payload, bytes):
            raise ValueError("PIHC3 generated country flags must provide byte payloads.")
        return artifact.payload

    def write(self, artifact: Artifact, output_root: object) -> str:
        """Write the prepared TGA bytes and return the target path."""

        target = pj(str(output_root), str(artifact.path))
        save_bin(self.render_bytes(artifact), target)
        return target


def build_family() -> PIHC3CountryFamily:
    """HeavenBase Registry target for the PIHC3 country compiler."""

    return PIHC3Country.build_family()


def _artifact_path(artifact: Artifact) -> str:
    return str(artifact.path).replace("\\", "/")


def _is_full_flag_path(path: str) -> bool:
    parts = path.split("/")
    return len(parts) == 3 and parts[:2] == ["gfx", "flags"] and parts[2].casefold().endswith(".tga")


def _scaled_flag_bytes(source_path: str, size: tuple[int, int]) -> bytes:
    with Image.open(source_path) as source:
        scaled = source.convert("RGBA").resize(size, Image.Resampling.LANCZOS)
        buffer = BytesIO()
        scaled.save(buffer, format="TGA")
    return buffer.getvalue()
