"""PIHC3 whole-project localisation reconciliation extension.

The migrated localisation baseline and native family localisation overlap by
design. This project-local postprocessor resolves those overlaps from canonical
planned artifacts before publication, so full, cached, and targeted builds all
publish the same final localisation graph.
"""

from __future__ import annotations

import hashlib
import os
import re
from collections.abc import Sequence
from dataclasses import dataclass, replace
from pathlib import Path, PurePosixPath

from heavenbase.utils import load_bin, save_bin

from paradev.build import (
    Artifact,
    BuildContext,
    BuildRegistry,
    LocalizationEntry,
    artifact_collection_ids,
    artifact_module_ids,
)
from paradev.games.hoi4.keywords import resolve_hoi4_game_root

HEADER_RE = re.compile(r"^\ufeff?\s*(?P<language>l_[A-Za-z0-9_]+)\s*:\s*$")
KEY_RE = re.compile(r"^\s*(?P<key>[^\s:#]+):\d*\s")
LEGACY_BASELINE_OWNER_PREFIX = "module:localization/"
POSTPROCESSOR_ID = "pihc3.localisation"
POSTPROCESSED_ARTIFACT_TYPE = "pihc3_localisation"


@dataclass(frozen=True, slots=True)
class _Entry:
    key: tuple[str, str]
    document_index: int
    path: str
    start: int
    end: int
    owner: str


@dataclass(frozen=True, slots=True)
class _Document:
    artifact: Artifact
    path: str
    text: str
    language: str


class PIHC3LocalisationWriter:
    """Write one already-reconciled PIHC3 localisation document."""

    artifact_type = POSTPROCESSED_ARTIFACT_TYPE

    def render_bytes(self, artifact: Artifact) -> bytes:
        """Return one reconciled localization document's exact final bytes.

        Args:
            artifact (Artifact): Reconciled PIHC3 localization artifact whose
                payload is already encoded for publication.

        Returns:
            bytes: Exact bytes to compare or publish.

        Raises:
            ValueError: If the postprocessor did not provide a byte payload.
        """

        if not isinstance(artifact.payload, bytes):
            raise ValueError("PIHC3 reconciled localisation artifacts must provide bytes.")
        return artifact.payload

    def write(self, artifact: Artifact, output_root: str | Path) -> Path:
        """Write the exact bytes prepared by the project postprocessor."""

        target = Path(output_root) / Path(str(artifact.path))
        save_bin(self.render_bytes(artifact), str(target))
        return target


class PIHC3LocalisationPostprocessor:
    """Resolve PIHC3 localisation precedence and replacement paths."""

    postprocessor_id = POSTPROCESSOR_ID

    def artifact_cache_key(self, _ctx: BuildContext) -> dict[str, object]:
        """Fingerprint every external HOI4 localization reference input."""

        return {
            "schema": "pihc3.localisation-reference-cache.v1",
            "roots": [_reference_root_fingerprint(root) for root in _reference_roots()],
        }

    def process(
        self,
        _ctx: BuildContext,
        artifacts: Sequence[Artifact],
    ) -> tuple[Artifact, ...]:
        """Return artifacts with a canonical project-wide localisation closure."""

        artifact_tuple = tuple(artifacts)
        documents = _localisation_documents(artifact_tuple)
        if not documents:
            return artifact_tuple
        reconciled = _deduplicate_documents(documents)
        reference_keys = _reference_keys(_reference_roots())
        transformed = _replacement_artifacts(reconciled, reference_keys=reference_keys)
        non_localisation = tuple(artifact for artifact in artifact_tuple if not _is_localisation_artifact(artifact))
        return (*non_localisation, *transformed)


def register(registry: BuildRegistry) -> None:
    """Register PIHC3 localisation publication behavior."""

    registry.add(PIHC3LocalisationWriter())
    registry.add(PIHC3LocalisationPostprocessor())


def _localisation_documents(artifacts: Sequence[Artifact]) -> tuple[_Document, ...]:
    documents: list[_Document] = []
    seen_paths: set[str] = set()
    for artifact in artifacts:
        if not _is_localisation_artifact(artifact):
            continue
        path = _artifact_path(artifact)
        if path in seen_paths:
            raise ValueError(f"PIHC3 localisation artifacts contain duplicate path {path!r}.")
        seen_paths.add(path)
        text, language = _validated_localisation_text(
            path=path,
            text=_artifact_text(artifact),
        )
        documents.append(
            _Document(
                artifact=artifact,
                path=path,
                text=text,
                language=language,
            )
        )
    return tuple(sorted(documents, key=lambda document: document.path))


def _is_localisation_artifact(artifact: Artifact) -> bool:
    if artifact.target_root != "output":
        return False
    path = PurePosixPath(_artifact_path(artifact))
    return len(path.parts) >= 3 and path.parts[0] == "localisation" and path.suffix == ".yml"


def _artifact_path(artifact: Artifact) -> str:
    return str(artifact.path).replace("\\", "/")


def _artifact_text(artifact: Artifact) -> str:
    if artifact.artifact_type == "loc":
        return "\ufeff" + _localisation_yml(_localisation_entries(artifact))
    if artifact.artifact_type == "copy":
        if len(artifact.inputs) != 1:
            raise ValueError("PIHC3 localisation copy artifacts must have exactly one input: " f"{_artifact_path(artifact)} has {len(artifact.inputs)}.")
        source_path = Path(artifact.inputs[0])
        return _strict_utf8_text(
            load_bin(str(source_path)),
            label=f"PIHC3 localisation copy input {source_path}",
        )
    raise ValueError("PIHC3 localisation postprocessing does not support artifact type " f"{artifact.artifact_type!r} at {_artifact_path(artifact)!r}.")


def _strict_utf8_text(payload: bytes, *, label: str) -> str:
    try:
        return payload.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError(f"{label} is not strict UTF-8 at byte {error.start}.") from error


def _validated_localisation_text(
    *,
    path: str,
    text: str,
) -> tuple[str, str]:
    body = text.removeprefix("\ufeff")
    if "\ufeff" in body:
        raise ValueError(f"PIHC3 localisation document contains an embedded or duplicate UTF-8 BOM: {path}.")
    lines = body.splitlines()
    if not lines:
        raise ValueError(f"PIHC3 localisation document is empty: {path}.")
    headers = [(index, match) for index, line in enumerate(lines) if (match := HEADER_RE.fullmatch(line)) is not None]
    if not headers:
        raise ValueError(f"PIHC3 localisation document must start with one valid l_* header: {path}.")
    if len(headers) > 1:
        header_lines = [index + 1 for index, _match in headers]
        raise ValueError(f"PIHC3 localisation document contains multiple language headers at lines {header_lines}: {path}.")
    header_index, header_match = headers[0]
    if header_index != 0:
        raise ValueError(f"PIHC3 localisation document must start with one valid l_* header: {path}.")

    language = header_match.group("language")
    path_language = _path_language(path)
    if language != path_language:
        raise ValueError(f"PIHC3 localisation header {language!r} does not match path language {path_language!r}: {path}.")
    normalized = "\ufeff" + body
    entries = _parse_entries(
        document_index=0,
        path=path,
        lines=normalized.splitlines(),
        owner="validation",
    )
    if any(entry.key[0] != language for entry in entries):
        raise ValueError(f"PIHC3 localisation entries do not all match header {language!r}: {path}.")
    return normalized, language


def _localisation_entries(artifact: Artifact) -> tuple[LocalizationEntry, ...]:
    payload = artifact.payload
    if not isinstance(payload, tuple) or not payload or not all(isinstance(entry, LocalizationEntry) for entry in payload):
        raise ValueError(f"PIHC3 localisation artifact has an invalid payload: {_artifact_path(artifact)}.")
    languages = {entry.language for entry in payload}
    if len(languages) != 1:
        raise ValueError(f"PIHC3 localisation artifact mixes languages: {_artifact_path(artifact)}.")
    return payload


def _localisation_yml(entries: tuple[LocalizationEntry, ...]) -> str:
    language = entries[0].language
    lines = [f"{language}:"]
    for entry in sorted(entries, key=lambda item: item.key):
        lines.append(f' {entry.key}:0 "{_localisation_escape(entry.text)}"')
    return "\n".join(lines) + "\n"


def _localisation_escape(value: str) -> str:
    normalized = value.replace("\r\n", "\n").replace("\r", "\n")
    return normalized.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def _deduplicate_documents(documents: tuple[_Document, ...]) -> tuple[_Document, ...]:
    entries_by_document: dict[int, tuple[_Entry, ...]] = {}
    entries_by_key: dict[tuple[str, str], list[_Entry]] = {}
    for document_index, document in enumerate(documents):
        entries = _document_entries(document, document_index=document_index)
        entries_by_document[document_index] = entries
        for entry in entries:
            entries_by_key.setdefault(entry.key, []).append(entry)

    duplicate_entries = (entries for entries in entries_by_key.values() if len(entries) > 1)
    keep = {
        min(
            entries,
            key=lambda entry: (
                _owner_priority(entry.owner),
                entry.path,
                entry.start,
            ),
        )
        for entries in duplicate_entries
    }
    remove = {entry for entries in entries_by_key.values() if len(entries) > 1 for entry in entries if entry not in keep}
    return tuple(
        replace(
            document,
            text=_rewrite_without_entries(
                document.text,
                tuple(entry for entry in entries_by_document[document_index] if entry in remove),
            ),
        )
        for document_index, document in enumerate(documents)
    )


def _document_entries(document: _Document, *, document_index: int) -> tuple[_Entry, ...]:
    entries = _parse_entries(
        document_index=document_index,
        path=document.path,
        lines=document.text.splitlines(),
        owner=document.artifact.owner,
    )
    if any(entry.key[0] != document.language for entry in entries):
        raise ValueError(f"PIHC3 localisation entries do not all match header {document.language!r}: {document.path}.")
    return entries


def _parse_entries(
    *,
    document_index: int,
    path: str,
    lines: list[str],
    owner: str,
) -> tuple[_Entry, ...]:
    entries: list[_Entry] = []
    index = 0
    language = _fallback_language(path)
    while index < len(lines):
        header_match = HEADER_RE.match(lines[index])
        if header_match:
            language = header_match.group("language")
            index += 1
            continue
        match = KEY_RE.match(lines[index])
        if not match or lines[index].lstrip().startswith("#"):
            index += 1
            continue
        start = index
        index += 1
        while index < len(lines):
            next_line = lines[index]
            if KEY_RE.match(next_line) and not next_line.lstrip().startswith("#"):
                break
            index += 1
        entries.append(
            _Entry(
                key=(language, match.group("key")),
                document_index=document_index,
                path=path,
                start=start,
                end=index,
                owner=owner,
            )
        )
    return tuple(entries)


def _owner_priority(owner: str) -> int:
    return int(owner.startswith(LEGACY_BASELINE_OWNER_PREFIX))


def _rewrite_without_entries(text: str, removed_entries: tuple[_Entry, ...]) -> str:
    if not removed_entries:
        return text
    has_bom = text.startswith("\ufeff")
    body = text[1:] if has_bom else text
    lines = body.splitlines()
    removed_by_start = {entry.start: entry for entry in removed_entries}
    output_lines: list[str] = []
    index = 0
    while index < len(lines):
        entry = removed_by_start.get(index)
        if entry is not None:
            index = entry.end
            continue
        output_lines.append(lines[index])
        index += 1
    suffix = "\n" if text.endswith("\n") else ""
    prefix = "\ufeff" if has_bom else ""
    return prefix + "\n".join(output_lines) + suffix


def _replacement_artifacts(
    documents: tuple[_Document, ...],
    *,
    reference_keys: set[tuple[str, str]],
) -> tuple[Artifact, ...]:
    grouped: dict[str, list[_Document]] = {}
    for document_index, document in enumerate(documents):
        entries = _document_entries(document, document_index=document_index)
        path = (
            _replacement_path(document.path)
            if not document.path.startswith("localisation/replace/")
            and document.artifact.metadata.get("family") != "state"
            and any(entry.key in reference_keys for entry in entries)
            else document.path
        )
        grouped.setdefault(path, []).append(document)
    return tuple(_merged_artifact(path, tuple(grouped[path])) for path in sorted(grouped))


def _replacement_path(path: str) -> str:
    parts = PurePosixPath(path).parts
    if len(parts) < 3 or parts[0] != "localisation" or parts[1] == "replace":
        raise ValueError(f"PIHC3 localisation replacement source has an invalid path: {path}.")
    return PurePosixPath("localisation", "replace", *parts[1:]).as_posix()


def _merged_artifact(path: str, documents: tuple[_Document, ...]) -> Artifact:
    languages = {document.language for document in documents}
    if len(languages) != 1:
        raise ValueError("PIHC3 localisation merge would combine different language headers " f"{sorted(languages)} at {path!r}.")
    ordered = tuple(
        sorted(
            documents,
            key=lambda document: (
                document.path != path,
                document.path,
            ),
        )
    )
    base = ordered[0].artifact
    text = ordered[0].text
    for document in ordered[1:]:
        text = _append_localisation_text(text, document.text)
    text, merged_language = _validated_localisation_text(path=path, text=text)
    if merged_language not in languages:
        raise ValueError(f"PIHC3 localisation merge changed language from {sorted(languages)!r} to {merged_language!r}: {path}.")

    views = tuple(document.artifact.to_dict() for document in ordered)
    module_ids = sorted({module_id for view in views for module_id in artifact_module_ids(view)})
    collection_ids = sorted({collection_id for view in views for collection_id in artifact_collection_ids(view)})
    families = {family for document in ordered for family in (document.artifact.metadata.get("family"),) if isinstance(family, str) and family}
    metadata = dict(base.metadata)
    metadata.pop("module_id", None)
    metadata.pop("collection_id", None)
    if module_ids:
        metadata["module_ids"] = module_ids
    if collection_ids:
        metadata["collection_ids"] = collection_ids
    if len(families) == 1:
        metadata["family"] = next(iter(families))
    else:
        metadata.pop("family", None)
    predecessor_paths = {document.path for document in ordered}
    for document in ordered:
        if document.artifact.metadata.get("family") == "state":
            # State aggregates intentionally shadow vanilla's exact file paths.
            # Retire the relocated copies emitted before this runtime fix.
            predecessor_paths.add(f"localisation/replace/{PurePosixPath(document.path).name}")
            predecessor_paths.add(PurePosixPath("localisation", "replace", *PurePosixPath(document.path).parts[1:]).as_posix())
        if path != document.path and not document.path.startswith("localisation/replace/"):
            predecessor_paths.add(f"localisation/replace/{PurePosixPath(document.path).name}")
    metadata.update(
        {
            "postprocessor_id": POSTPROCESSOR_ID,
            "publication_scope": "project",
            "publication_replaces": sorted(predecessor_paths),
            "source_owners": sorted({document.artifact.owner for document in ordered}),
        }
    )
    inputs = tuple(dict.fromkeys(source for document in ordered for source in document.artifact.inputs))
    return Artifact(
        path=path,
        artifact_type=POSTPROCESSED_ARTIFACT_TYPE,
        owner=base.owner,
        inputs=inputs,
        mode=base.mode,
        target_root="output",
        metadata=metadata,
        payload=text.encode("utf-8"),
    )


def _append_localisation_text(target_text: str, source_text: str) -> str:
    target = target_text.removeprefix("\ufeff")
    source = source_text.removeprefix("\ufeff")
    source_lines = source.splitlines()
    if source_lines and HEADER_RE.match(source_lines[0]):
        source_lines = source_lines[1:]
    append_text = "\n".join(source_lines)
    if append_text:
        separator = "" if target.endswith("\n") else "\n"
        suffix = "\n" if source.endswith("\n") else ""
        target += separator + append_text + suffix
    return "\ufeff" + target


def _fallback_language(path: str) -> str:
    return _path_language(path)


def _path_language(path: str) -> str:
    language = _identified_path_language(path)
    if language is None:
        raise ValueError(f"PIHC3 localisation path does not identify a language: {path}.")
    return language


def _identified_path_language(path: str) -> str | None:
    artifact_path = PurePosixPath(path)
    parts = artifact_path.parts
    if len(parts) < 2 or parts[0] != "localisation":
        raise ValueError(f"PIHC3 localisation path does not identify a language: {path}.")

    candidates: list[str] = []
    match = re.search(r"_(l_[A-Za-z0-9_]+)\.ya?ml$", artifact_path.name)
    if match:
        candidates.append(match.group(1))

    relative_parts = parts[1:]
    if relative_parts[0] == "replace":
        relative_parts = relative_parts[1:]
    if len(relative_parts) >= 2:
        folder = relative_parts[0]
        if not re.fullmatch(r"[A-Za-z0-9_]+", folder):
            raise ValueError(f"PIHC3 localisation path has an invalid language folder {folder!r}: {path}.")
        candidates.append(folder if folder.startswith("l_") else f"l_{folder}")

    languages = set(candidates)
    if not languages:
        return None
    if len(languages) != 1:
        raise ValueError(f"PIHC3 localisation path identifies conflicting languages {sorted(languages)}: {path}.")
    return next(iter(languages))


def _reference_roots() -> tuple[Path, ...]:
    environment_root = os.environ.get("PIHC3_HOI4_GAME_ROOT")
    root = resolve_hoi4_game_root(environment_root if environment_root and environment_root.strip() else None)
    return (root,) if root is not None and root.exists() else ()


def _reference_keys(reference_roots: tuple[Path, ...]) -> set[tuple[str, str]]:
    keys: set[tuple[str, str]] = set()
    for root in reference_roots:
        for localisation_root in _reference_localisation_roots(root):
            for path in sorted(localisation_root.rglob("*.yml")):
                relative = path.relative_to(localisation_root).as_posix()
                document_path = f"localisation/{relative}"
                reference_text = _strict_utf8_text(
                    load_bin(str(path)),
                    label=f"HOI4 reference localisation {path}",
                )
                keys.update(_reference_document_keys(path=document_path, text=reference_text))
    return keys


def _reference_root_fingerprint(root: Path) -> dict[str, object]:
    """Return a content digest for one external localization reference root."""

    digest = hashlib.sha256()
    file_count = 0
    for localisation_root in _reference_localisation_roots(root):
        resolved_root = localisation_root.resolve()
        digest.update(str(resolved_root).encode("utf-8"))
        digest.update(b"\0")
        for path in sorted(localisation_root.rglob("*.yml")):
            if not path.is_file():
                continue
            relative = path.relative_to(localisation_root).as_posix().encode("utf-8")
            digest.update(len(relative).to_bytes(8, "big"))
            digest.update(relative)
            file_digest = hashlib.sha256()
            with path.open("rb") as handle:
                while chunk := handle.read(1024 * 1024):
                    file_digest.update(chunk)
            digest.update(file_digest.digest())
            file_count += 1
    return {
        "root": str(root.resolve()),
        "file_count": file_count,
        "sha256": digest.hexdigest(),
    }


def _reference_document_keys(*, path: str, text: str) -> set[tuple[str, str]]:
    body = text.removeprefix("\ufeff")
    if "\ufeff" in body:
        raise ValueError(f"HOI4 reference localisation contains an embedded or duplicate UTF-8 BOM: {path}.")
    lines = body.splitlines()
    language: str | None = None
    languages: set[str] = set()
    keys: set[tuple[str, str]] = set()
    for line_number, line in enumerate(lines, start=1):
        header_match = HEADER_RE.fullmatch(line)
        if header_match is not None:
            language = header_match.group("language")
            languages.add(language)
            continue
        key_match = KEY_RE.match(line)
        if key_match is None or line.lstrip().startswith("#"):
            continue
        if language is None:
            raise ValueError(f"HOI4 reference localisation has an active key before any language header at line {line_number}: {path}.")
        keys.add((language, key_match.group("key")))

    if not languages:
        if all(not line.strip() or line.lstrip().startswith("#") for line in lines):
            return set()
        raise ValueError(f"HOI4 reference localisation has active content but no valid l_* header: {path}.")
    path_language = _identified_path_language(path)
    if path_language is not None and languages != {path_language}:
        raise ValueError(f"HOI4 reference localisation headers {sorted(languages)} do not match path language {path_language!r}: {path}.")
    return keys


def _reference_localisation_roots(root: Path) -> tuple[Path, ...]:
    if not root.exists():
        return ()
    if root.name == "localisation":
        return (root,)
    localisation_root = root / "localisation"
    if localisation_root.exists():
        return (localisation_root,)
    return (root,)
