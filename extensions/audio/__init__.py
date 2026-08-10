"""PIHC3 audio Entity extension."""

from __future__ import annotations

import heavenbase as hb

from paradev.build import SimpleSourceFamily, Slot


class PIHC3AudioModule(hb.Entity):
    """One independently editable PIHC3 audio module."""

    identifier = "pihc3-audio-module"
    module_id = (
        hb.field(hb.ShortText).default("").desc("Stable ParaDev module identifier.")
    )
    data = (
        hb.field(hb.Json)
        .default({})
        .desc("Structured metadata, localization, and resource references.")
    )
    family = "audio"
    resource_slots = (
        Slot(
            name="pdx",
            match="^(music/.*\\.(txt|asset)|sound/.*\\.asset|dlc/[^/]+/music/.*\\.txt|integrated_dlc/[^/]+/music/.*\\.txt)$",
            required=True,
            many=True,
            regex=True,
            kind="pdx",
        ),
        Slot(
            name="assets",
            match="^music/.*\\.ogg$",
            many=True,
            regex=True,
            kind="copy",
            authoring_path="music/{filename}",
        ),
        Slot(
            name="assets",
            match="^sound/.*\\.(wav|ogg)$",
            many=True,
            regex=True,
            kind="copy",
            authoring_path="sound/{filename}",
        ),
        Slot(
            name="assets",
            match="^gfx/music/.*\\.dds$",
            many=True,
            regex=True,
            kind="copy",
            authoring_path="gfx/music/{filename}",
        ),
    )
    compilation_hooks = ("normalize", "check", "emit")


def build_family() -> SimpleSourceFamily:
    """Return the Registry compiler owned by this Entity extension."""

    return SimpleSourceFamily(
        family=PIHC3AudioModule.family,
        source_slots=PIHC3AudioModule.resource_slots,
        pdx_path_template="{source_path}",
        copy_path_template="{source_path}",
        visible=False,
    )


__all__ = ["PIHC3AudioModule", "build_family"]
