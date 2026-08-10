"""PIHC3 loading screen Entity extension."""

from __future__ import annotations

import heavenbase as hb

from paradev.build import SimpleSourceFamily, Slot


class PIHC3LoadingScreenModule(hb.Entity):
    """One independently editable PIHC3 loading screen module."""

    identifier = "pihc3-loading-screen-module"
    module_id = (
        hb.field(hb.ShortText).default("").desc("Stable ParaDev module identifier.")
    )
    data = (
        hb.field(hb.Json)
        .default({})
        .desc("Structured metadata, localization, and resource references.")
    )
    family = "loading_screen"
    resource_slots = (
        Slot(
            name="assets",
            match="^gfx/loadingscreens/.*\\.dds$",
            required=True,
            many=True,
            regex=True,
            kind="copy",
            authoring_path="gfx/loadingscreens/{filename}",
        ),
    )
    compilation_hooks = ("normalize", "check", "emit")


def build_family() -> SimpleSourceFamily:
    """Return the Registry compiler owned by this Entity extension."""

    return SimpleSourceFamily(
        family=PIHC3LoadingScreenModule.family,
        source_slots=PIHC3LoadingScreenModule.resource_slots,
        copy_path_template="{source_path}",
        visible=False,
    )


__all__ = ["PIHC3LoadingScreenModule", "build_family"]
