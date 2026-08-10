"""PIHC3 compiler overlay for the built-in event family."""

from __future__ import annotations

from typing import ClassVar

from paradev.build import Slot
from paradev.games.hoi4 import EventFamily

EVENT_RESOURCE_SLOTS = (
    Slot("def", "def.txt", kind="pdx"),
    Slot("loc", "**/*.loc", many=True, kind="loc"),
    Slot("preview", "preview.png"),
    Slot(
        "compiled_assets",
        r"^gfx/event_pictures/.*\.dds$",
        many=True,
        regex=True,
        kind="copy",
        authoring_path="gfx/event_pictures/{filename}",
    ),
    Slot(
        "compiled_assets",
        r"^interface/events/.*\.gfx$",
        many=True,
        regex=True,
        kind="copy",
        authoring_path="interface/events/{filename}",
    ),
)

EVENT_SOURCE_FORM_FIELD_HINTS = {
    "picture": {
        "description": {
            "default": "Event-picture sprite identifier shown in the event window.",
            "zh": "事件窗口中显示的事件图片精灵标识。",
        }
    },
    "is_triggered_only": {
        "description": {
            "default": "Whether the event can fire only when invoked by script.",
            "zh": "该事件是否只能由脚本调用触发。",
        }
    },
    "fire_only_once": {
        "description": {
            "default": "Whether this event may fire only once per game.",
            "zh": "该事件是否每局游戏只能触发一次。",
        }
    },
    "hidden": {
        "description": {
            "default": "Whether the event executes without showing an event window.",
            "zh": "该事件是否不显示事件窗口而直接执行。",
        }
    },
}


class PIHC3EventFamily(EventFamily):
    """Add PIHC3 event-picture routing to the built-in event family."""

    replaces_registered_family = True
    source_form_field_hints: ClassVar[dict[str, dict[str, object]]] = EVENT_SOURCE_FORM_FIELD_HINTS

    def __init__(self) -> None:
        super().__init__(
            family="event",
            pdx_path_template="events/{collection_id}.txt",
            module_pdx_path_template="events/{object_id}.txt",
            loc_path_template=("localisation/{language_folder}/{object_id}_{language}.yml"),
            copy_path_template="{source_path}",
            source_slots=EVENT_RESOURCE_SLOTS,
        )


def build_family() -> PIHC3EventFamily:
    """Return the PIHC3 overlay for the built-in event family."""

    return PIHC3EventFamily()
