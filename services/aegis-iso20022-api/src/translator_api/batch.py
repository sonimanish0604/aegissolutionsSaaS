from __future__ import annotations

import io
import re
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List


class BatchParseError(ValueError):
    """Raised when a batch payload cannot be parsed."""


@dataclass
class BatchMessage:
    index: int
    mt_raw: str


@dataclass
class BatchFile:
    source_name: str
    header: Dict[str, str]
    trailer: Dict[str, str]
    messages: List[BatchMessage]


_MESSAGE_SPLIT = re.compile(r"\n\$\s*\n", re.MULTILINE)


def _parse_kv_line(line: str, expected_prefix: str) -> Dict[str, str]:
    line = line.strip()
    if not line:
        raise BatchParseError(f"Missing {expected_prefix} line")
    parts = line.split("|")
    if not parts or parts[0] != expected_prefix:
        raise BatchParseError(f"Expected line to start with '{expected_prefix}|', got: {line!r}")
    data: Dict[str, str] = {}
    for segment in parts[1:]:
        if not segment:
            continue
        if "=" not in segment:
            continue
        key, value = segment.split("=", 1)
        data[key] = value
    return data


def parse_batch_dat(text: str, source_name: str) -> BatchFile:
    normalized = text.replace("\r\n", "\n").strip()
    if not normalized:
        raise BatchParseError(f"{source_name}: batch content is empty")

    lines = normalized.splitlines()
    if len(lines) < 3:
        raise BatchParseError(f"{source_name}: expected header, messages, and trailer lines")

    header_line = lines[0]
    trailer_line = lines[-1]
    body = "\n".join(lines[1:-1]).strip()

    header = _parse_kv_line(header_line, "HDR")
    if "CreateDate" in header:
        raw_date = header["CreateDate"]
        if len(raw_date) == 10:
            header["CreateDate"] = raw_date
        else:
            header["CreateDate"] = raw_date
    trailer = _parse_kv_line(trailer_line, "TRL")

    if not body:
        raise BatchParseError(f"{source_name}: no MT messages found in batch body")

    segments = _MESSAGE_SPLIT.split(body)
    messages: List[BatchMessage] = []
    for segment in segments:
        segment = segment.strip()
        if not segment:
            continue
        messages.append(BatchMessage(index=len(messages) + 1, mt_raw=segment))

    if not messages:
        raise BatchParseError(f"{source_name}: no MT messages found in batch body")

    return BatchFile(
        source_name=source_name,
        header=header,
        trailer=trailer,
        messages=messages,
    )


def parse_batch_payload(filename: str, data: bytes) -> List[BatchFile]:
    if not data:
        raise BatchParseError("Uploaded file is empty")

    suffix = Path(filename or "").suffix.lower()

    if suffix == ".zip":
        try:
            zf = zipfile.ZipFile(io.BytesIO(data))
        except zipfile.BadZipFile as exc:
            raise BatchParseError("Provided ZIP archive is invalid") from exc
        batches: List[BatchFile] = []
        for info in zf.infolist():
            if info.is_dir():
                continue
            inner_path = Path(info.filename)
            if inner_path.suffix.lower() not in {".dat", ".txt"}:
                continue
            content = zf.read(info)
            try:
                text = content.decode("utf-8")
            except UnicodeDecodeError:
                text = content.decode("latin-1")
            batches.append(parse_batch_dat(text, inner_path.name))
        if not batches:
            raise BatchParseError("ZIP archive does not contain any .dat or .txt batch files")
        return batches

    if suffix in {".dat", ".txt"}:
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            text = data.decode("latin-1")
        return [parse_batch_dat(text, Path(filename or 'batch.dat').name)]

    raise BatchParseError("Unsupported file type. Provide .dat, .txt, or .zip containing batch files.")
