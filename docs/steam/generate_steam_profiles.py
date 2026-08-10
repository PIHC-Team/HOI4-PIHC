"""Generate trimmed Steam markup from the bilingual PIHC3 player profiles."""

from __future__ import annotations

import argparse
import shlex
import sys

from heavenbase.utils import (
    cmd,
    exists_file,
    get_file_basename,
    get_file_dir,
    load_txt,
    pj,
    save_txt,
)

PROFILE_ROOT = get_file_dir(__file__)
STEAMDOWN_VERSION = "0.2.1"
STEAM_UPDATE_COUNT = 2
MORE = {
    "en": "See full documentation for more details.",
    "zh": "详见完整版文档。",
}
INTRO = """[h2] Both English and Chinese are supported! 中英文支持！ [/h2]

[h2][url=https://drive.google.com/file/d/1kHr0KarnZwIWu95U-9BfMzLN-cupUKLD/view?usp=sharing]Full English Documentation[/url][/h2]
[h2][url=https://drive.google.com/file/d/1J3C3PZd9dliNcITBB1DX_YKaopArv1C5/view?usp=sharing]完整中文文档[/url][/h2]

Discord: [url=https://discord.gg/VzUUMF9af5][/url]
QQ Group: 934449651, 870730772, 1060929496 (Vic3)

"""


def main() -> None:
    """Generate both localized Steam profiles or verify they are current."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail when generated Steam markup differs instead of writing it.",
    )
    parser.add_argument(
        "--steamdown-command",
        help=(
            "Command used to convert Markdown to Steam markup. Defaults to "
            f"npx steamdown@{STEAMDOWN_VERSION}."
        ),
    )
    args = parser.parse_args()

    command = resolve_steamdown(args.steamdown_command)
    stale: list[str] = []
    for language in MORE:
        source = pj(PROFILE_ROOT, f"STEAM_PROFILE.{language}.md")
        output = pj(PROFILE_ROOT, f"STEAM_PROFILE.steam.{language}.md")
        generated = (
            trim_steam_readme(convert_markdown(source, command), language).rstrip("\n")
            + "\n"
        )
        if args.check:
            if (
                not exists_file(output)
                or load_txt(output, encoding="utf-8") != generated
            ):
                stale.append(output)
            continue
        save_txt(generated.rstrip("\n"), output, encoding="utf-8")
        print(f"Generated {get_file_basename(output)}")

    if stale:
        names = ", ".join(get_file_basename(path) for path in stale)
        print(f"Generated Steam profiles are stale: {names}", file=sys.stderr)
        raise SystemExit(1)


def resolve_steamdown(value: str | None) -> list[str]:
    """Resolve the Steam Markdown converter command.

    Args:
        value: Optional shell-style command supplied by the caller.

    Returns:
        The executable and arguments used to invoke Steamdown.

    Raises:
        SystemExit: If an explicitly supplied command is empty.
    """
    if value:
        command = shlex.split(value)
        if command:
            return command
        raise SystemExit("--steamdown-command must not be empty")

    return ["npx", "--yes", f"steamdown@{STEAMDOWN_VERSION}"]


def convert_markdown(source: str, command: list[str]) -> str:
    """Convert one Markdown README to Steam markup.

    Args:
        source: Markdown source file.
        command: Steamdown executable and arguments.

    Returns:
        Steam markup emitted by the converter.

    Raises:
        CalledProcessError: If Steamdown exits unsuccessfully.
    """
    output = cmd(
        command,
        input=load_txt(source, encoding="utf-8"),
        check=True,
        include="out",
    )
    return f"{output}\n"


def trim_steam_readme(content: str, language: str) -> str:
    """Trim a full Steamdown document to the Steam description format.

    Args:
        content: Full Steam markup produced by Steamdown.
        language: Documentation language, either ``en`` or ``zh``.

    Returns:
        The compact Steam description with only the two newest log entries.

    Raises:
        ValueError: If the requested language is unsupported.
    """
    if language not in MORE:
        raise ValueError(f"unsupported README language: {language}")

    sections = split_tagged(content, "[h2]")
    trimmed = [INTRO]
    for section in sections:
        if starts_with_any(section, "[h2]Update Log[/h2]", "[h2]更新日志[/h2]"):
            updates = split_tagged(section, "[h3]")
            trimmed.append(
                "".join(updates[: STEAM_UPDATE_COUNT + 1])
                + f"...\n{MORE[language]}\n\n"
            )
        elif starts_with_any(section, "[h2]Acknowledgement[/h2]", "[h2]致谢[/h2]"):
            acknowledgement = section.split("    [*]Expanded Resources", maxsplit=1)[0]
            trimmed.append(acknowledgement + f"[/list]\n...\n{MORE[language]}\n\n")
        elif starts_with_any(
            section, "[h2]Non-steam Installation[/h2]", "[h2]非Steam安装[/h2]"
        ):
            continue
        elif starts_with_any(
            section,
            "[h2]WE NEED YOU[/h2]",
            "[h2]我们需要你[/h2]",
            "[h2]Contact[/h2]",
            "[h2]联系方式[/h2]",
        ):
            continue
        elif starts_with_any(
            section,
            "[h2]About HOI4DEV[/h2]",
            "[h2]关于HOI4DEV[/h2]",
            "[h2]Develop PIHC3 with ParaDev[/h2]",
            "[h2]使用 ParaDev 开发 PIHC3[/h2]",
        ):
            heading = section.splitlines()[0]
            trimmed.append(f"{heading}\n{MORE[language]}\n\n")
        else:
            trimmed.append(section)

    return (
        "".join(trimmed)
        .replace('<input checked="" disabled="" type="checkbox">', "")
        .replace('<input disabled="" type="checkbox">', "")
    )


def split_tagged(content: str, tag: str) -> list[str]:
    """Split markup while retaining the tag at each section boundary."""
    parts = content.split(tag)
    return [parts[0], *(tag + part for part in parts[1:])]


def starts_with_any(value: str, *prefixes: str) -> bool:
    """Return whether a string begins with one of the supplied prefixes."""
    return value.startswith(prefixes)


if __name__ == "__main__":
    main()
