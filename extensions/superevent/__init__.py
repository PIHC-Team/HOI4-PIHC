"""PIHC3 superevent Entity extension."""

from __future__ import annotations

import heavenbase as hb

from paradev.build import SimpleSourceFamily, Slot

_SOURCE_FORM_FIELD_HINTS = {
    "add_namespace": {
        "label": {"default": "Event namespace", "zh": "事件命名空间"},
        "description": {
            "default": "Namespace registered for the hidden superevent or its paired news event.",
            "zh": "为隐藏超级事件或其配对新闻事件注册的命名空间。",
        },
    },
    "id": {
        "label": {"default": "Event ID", "zh": "事件 ID"},
        "description": {
            "default": "Stable namespace-qualified identifier for this event record.",
            "zh": "此事件记录的稳定命名空间限定标识。",
        },
    },
    "title": {
        "label": {"default": "Title key", "zh": "标题文本键"},
        "description": {
            "default": "Localization key displayed as the event title.",
            "zh": "作为事件标题显示的本地化键。",
        },
    },
    "desc": {
        "label": {"default": "Description key", "zh": "描述文本键"},
        "description": {
            "default": "Localization key displayed as the event description.",
            "zh": "作为事件描述显示的本地化键。",
        },
    },
    "picture": {
        "label": {"default": "Event picture", "zh": "事件图片"},
        "description": {
            "default": "GFX event-picture sprite shown for this superevent or news event.",
            "zh": "此超级事件或新闻事件显示的 GFX 事件图片精灵。",
        },
    },
    "is_triggered_only": {
        "label": {"default": "Script-triggered only", "zh": "仅脚本触发"},
        "description": {
            "default": "Whether this event can fire only when another script invokes it.",
            "zh": "此事件是否只能由其他脚本调用触发。",
        },
    },
    "fire_only_once": {
        "label": {"default": "Fire only once", "zh": "仅触发一次"},
        "description": {
            "default": "Whether the hidden superevent may run only once per game.",
            "zh": "隐藏超级事件是否每局游戏只能运行一次。",
        },
    },
    "hidden": {
        "label": {"default": "Hidden event", "zh": "隐藏事件"},
        "description": {
            "default": "Whether the event executes without a normal event window.",
            "zh": "此事件是否不显示普通事件窗口而直接执行。",
        },
    },
    "major": {
        "label": {"default": "Major news", "zh": "重大新闻"},
        "description": {
            "default": "Whether the paired news event is presented as major news.",
            "zh": "配对新闻事件是否作为重大新闻显示。",
        },
    },
    "immediate": {
        "label": {"default": "Immediate effects", "zh": "立即效果"},
        "description": {
            "default": "Effects executed as soon as this event fires.",
            "zh": "此事件触发后立即执行的效果。",
        },
        "control": "block-text",
    },
    "option": {
        "label": {"default": "Event option", "zh": "事件选项"},
        "description": {
            "default": "One selectable or automatically resolved event outcome.",
            "zh": "一条可选择或自动结算的事件结果。",
        },
        "control": "block-text",
    },
    "trigger": {
        "label": {"default": "Option conditions", "zh": "选项条件"},
        "description": {
            "default": "Conditions controlling whether this event option is available.",
            "zh": "控制此事件选项是否可用的条件。",
        },
        "control": "block-text",
    },
}


class PIHC3SupereventModule(hb.Entity):
    """One independently editable PIHC3 superevent module."""

    identifier = "pihc3-superevent-module"
    module_id = (
        hb.field(hb.ShortText).default("").desc("Stable ParaDev module identifier.")
    )
    data = (
        hb.field(hb.Json)
        .default({})
        .desc("Structured metadata, localization, and resource references.")
    )
    family = "superevent"
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
            name="pictures",
            match="pictures/*.dds",
            many=True,
            kind="copy",
            authoring_path="pictures/{filename}",
        ),
    )
    compilation_hooks = ("normalize", "check", "emit")
    source_form_field_hints = _SOURCE_FORM_FIELD_HINTS

    @classmethod
    def build_family(cls) -> PIHC3SupereventFamily:
        """Return the superevent compiler owned by this Entity extension."""

        return PIHC3SupereventFamily()


class PIHC3SupereventFamily(SimpleSourceFamily):
    """Compile PIHC3 superevent pairs, localization, and pictures."""

    source_form_field_hints = _SOURCE_FORM_FIELD_HINTS

    def __init__(self) -> None:
        super().__init__(
            family=PIHC3SupereventModule.family,
            source_slots=PIHC3SupereventModule.resource_slots,
            sprite_slots=("pictures",),
            required_loc_keys=(
                "EVENT_SUPER_{object_id}_NAME",
                "EVENT_SUPER_{object_id}_DESC",
                "EVENT_SUPER_{object_id}_MARK",
                "EVENT_SUPER_{object_id}_NEWS_NAME",
                "EVENT_SUPER_{object_id}_NEWS_DESC",
                "EVENT_SUPER_{object_id}_NEWS_o",
            ),
            pdx_path_template="events/SUPEREVENT_{object_id}.txt",
            loc_path_template=(
                "localisation/{language_folder}/EVENT_SUPER_{object_id}_{language}.yml"
            ),
            copy_path_template="gfx/event_pictures/{source_name}",
            sprite_gfx_path_template="interface/PIHC3_superevents.gfx",
            sprite_name_template="GFX_{source_stem}",
        )


def build_family() -> PIHC3SupereventFamily:
    """Materialize the superevent compiler through HeavenBase."""

    return PIHC3SupereventModule.build_family()


__all__ = ["PIHC3SupereventFamily", "PIHC3SupereventModule", "build_family"]
