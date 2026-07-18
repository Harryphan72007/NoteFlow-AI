from __future__ import annotations

import re
import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile

from ..config import settings


SAFE_NAME = re.compile(r"[^A-Za-z0-9._-]+")


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


async def save_upload(file: UploadFile, *, allowed: set[str], max_mb: int, subdir: str) -> tuple[Path, bytes]:
    validate_extension(file.filename or "", allowed)
    body = await file.read()
    if not body:
        raise HTTPException(status_code=422, detail="Uploaded file is empty")
    if len(body) > max_mb * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"File exceeds {max_mb} MB limit")

    target_dir = settings.upload_dir / subdir
    target_dir.mkdir(parents=True, exist_ok=True)
    target = ensure_within(target_dir, target_dir / f"{uuid4().hex}_{safe_filename(file.filename or 'upload.bin')}")
    target.write_bytes(body)
    return target, body


def copy_to_export(source: Path, export_name: str) -> Path:
    target = ensure_within(settings.export_dir, settings.export_dir / safe_filename(export_name))
    shutil.copyfile(source, target)
    return target
