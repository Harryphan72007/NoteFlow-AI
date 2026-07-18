from __future__ import annotations

import re
import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile

from ..config import settings


SAFE_NAME = re.compile(r"[^A-Za-z0-9._-]+")

CONTENT_KIND_BY_SUFFIX = {
    "txt": "text",
    "wav": "wav",
    "mp3": "mp3",
    "m4a": "m4a",
    "flac": "flac",
    "ogg": "ogg",
    "webm": "webm",
    "jpg": "jpeg",
    "jpeg": "jpeg",
    "png": "png",
    "webp": "webp",
    "tif": "tiff",
    "tiff": "tiff",
    "pdf": "pdf",
}


def safe_filename(filename: str) -> str:
    cleaned = SAFE_NAME.sub("_", Path(filename).name).strip("._")
    return cleaned or "upload.bin"


def ensure_within(base: Path, target: Path) -> Path:
    base_resolved = base.resolve()
    target_resolved = target.resolve()
    if base_resolved != target_resolved and base_resolved not in target_resolved.parents:
        raise HTTPException(status_code=400, detail="Invalid storage path")
    return target_resolved


def validate_extension(filename: str, allowed: set[str]) -> str:
    suffix = Path(filename).suffix.lower().lstrip(".")
    if suffix not in allowed:
        raise HTTPException(status_code=415, detail=f"Unsupported file extension: {suffix or 'none'}")
    return suffix


def sniff_content_kind(body: bytes) -> str | None:
    if body.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if body.startswith(b"\xff\xd8\xff"):
        return "jpeg"
    if body.startswith((b"II*\x00", b"MM\x00*")):
        return "tiff"
    if body.startswith(b"%PDF-"):
        return "pdf"
    if body.startswith(b"fLaC"):
        return "flac"
    if body.startswith(b"OggS"):
        return "ogg"
    if body.startswith(b"\x1aE\xdf\xa3"):
        return "webm"
    if body.startswith(b"RIFF") and body[8:12] == b"WAVE":
        return "wav"
    if body.startswith(b"RIFF") and body[8:12] == b"WEBP":
        return "webp"
    if len(body) >= 12 and body[4:8] == b"ftyp":
        return "m4a"
    if body.startswith(b"ID3") or (len(body) >= 2 and body[0] == 0xFF and body[1] & 0xE0 == 0xE0):
        return "mp3"
    if b"\x00" not in body[:4096]:
        try:
            body.decode("utf-8")
            return "text"
        except UnicodeDecodeError:
            pass
    return None


def validate_content(body: bytes, suffix: str) -> str:
    expected = CONTENT_KIND_BY_SUFFIX.get(suffix)
    actual = sniff_content_kind(body)
    if expected is None or actual != expected:
        raise HTTPException(
            status_code=415,
            detail=f"File content does not match .{suffix} extension",
        )
    return actual


async def save_upload(file: UploadFile, *, allowed: set[str], max_mb: int, subdir: str) -> tuple[Path, bytes]:
    suffix = validate_extension(file.filename or "", allowed)
    body = await file.read()
    if not body:
        raise HTTPException(status_code=422, detail="Uploaded file is empty")
    if len(body) > max_mb * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"File exceeds {max_mb} MB limit")
    validate_content(body, suffix)

    target_dir = settings.upload_dir / subdir
    target_dir.mkdir(parents=True, exist_ok=True)
    target = ensure_within(target_dir, target_dir / f"{uuid4().hex}_{safe_filename(file.filename or 'upload.bin')}")
    target.write_bytes(body)
    return target, body


def copy_to_export(source: Path, export_name: str) -> Path:
    target = ensure_within(settings.export_dir, settings.export_dir / safe_filename(export_name))
    shutil.copyfile(source, target)
    return target
