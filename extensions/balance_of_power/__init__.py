"""PIHC3 balance of power Entity extension."""

from __future__ import annotations

import heavenbase as hb

from paradev.build import SimpleSourceFamily, Slot


class PIHC3BalanceOfPowerModule(hb.Entity):
    """One independently editable PIHC3 balance of power module."""

    identifier = "pihc3-balance-of-power-module"
    module_id = (
        hb.field(hb.ShortText).default("").desc("Stable ParaDev module identifier.")
    )
    data = (
        hb.field(hb.Json)
        .default({})
        .desc("Structured metadata, localization, and resource references.")
    )
    family = "balance_of_power"
    resource_slots = (
        Slot(
            name="def",
            match="def.txt",
            required=True,
            kind="pdx",
        ),
        Slot(
            name="loc",
            match="**/*.loc",
            many=True,
            kind="loc",
        ),
        Slot(
            name="assets",
            match="^gfx/interface/bop/.*\\.dds$",
            many=True,
            regex=True,
            kind="copy",
            authoring_path="gfx/interface/bop/{filename}",
        ),
        Slot(
            name="assets",
            match="^interface/bop/.*\\.gfx$",
            many=True,
            regex=True,
            kind="copy",
            authoring_path="interface/bop/{filename}",
        ),
    )
    compilation_hooks = ("normalize", "check", "emit")


def build_family() -> SimpleSourceFamily:
    """Return the Registry compiler owned by this Entity extension."""

    return SimpleSourceFamily(
        family=PIHC3BalanceOfPowerModule.family,
        source_slots=PIHC3BalanceOfPowerModule.resource_slots,
        pdx_path_template="common/bop/{object_id}.txt",
        loc_path_template="localisation/{language_folder}/{object_id}_{language}.yml",
        copy_path_template="{source_path}",
        required_loc_keys=("{object_id}", "{object_id}_desc"),
    )


__all__ = ["PIHC3BalanceOfPowerModule", "build_family"]
