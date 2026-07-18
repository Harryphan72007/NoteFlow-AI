from __future__ import annotations

import ast
import os
import subprocess
import threading
from pathlib import Path

import imageio_ffmpeg

from ..config import settings


class ASRServiceError(RuntimeError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


_INFERENCE_LOCK = threading.Lock()


def using_small_cpu_model() -> bool:
    return settings.asr_model_mode.strip().lower() in {
        "qwen3-asr-0.6b",
        "qwen3-asr-small",
        "small",
    }


def asr_runtime_requirements() -> tuple[Path, ...]:
    if using_small_cpu_model():
        return (
            settings.mega_asr_python,
            Path(__file__).with_name("asr_small_runner.py"),
            settings.qwen_asr_small_model_dir,
            settings.qwen_asr_small_model_dir / "config.json",
        )
    return (
        settings.mega_asr_python,
        settings.mega_asr_root / "infer.py",
        settings.mega_asr_ckpt_dir / "Qwen3-ASR-1.7B",
        settings.mega_asr_ckpt_dir / "mega-asr-merged",
        settings.mega_asr_ckpt_dir / "audio_quality_router" / "best_acc_model.safetensors",
    )


def _error_code(output: str) -> str:
    lowered = output.lower()
    if "out of memory" in lowered or "cannot allocate memory" in lowered:
        return "out_of_memory"
    if "decode" in lowered or "unsupported format" in lowered:
        return "decode_error"
    if "loading checkpoint" in lowered or "model_loading" in lowered:
        return "model_loading"
    return "transcription_error"


def _parse_result(stdout: str) -> dict:
    for line in reversed(stdout.splitlines()):
        candidate = line.strip()
        if not candidate.startswith("{"):
            continue
        try:
            parsed = ast.literal_eval(candidate)
        except (SyntaxError, ValueError):
            continue
        if isinstance(parsed, dict) and "text" in parsed:
            values = parsed["text"]
            text = " ".join(str(value).strip() for value in values) if isinstance(values, list) else str(values).strip()
            if text:
                parsed["text"] = text
                return parsed
    raise ASRServiceError("transcription_error", "ASR model returned no non-empty transcript")


def _transcode_to_wav(path: Path) -> Path:
    target = path.with_name(f"{path.name}.asr.wav")
    command = [
        imageio_ffmpeg.get_ffmpeg_exe(),
        "-y",
        "-i",
        str(path),
        "-ac",
        "1",
        "-ar",
        "16000",
        str(target),
    ]
    try:
        completed = subprocess.run(command, capture_output=True, text=True, timeout=180, check=False)
    except subprocess.TimeoutExpired as exc:
        raise ASRServiceError("decode_error", "Audio conversion timed out") from exc
    if completed.returncode != 0 or not target.exists():
        target.unlink(missing_ok=True)
        message = completed.stderr.strip()[-2000:] or "Audio conversion failed"
        raise ASRServiceError("decode_error", message)
    return target


def transcribe_audio(path: Path) -> dict:
    missing = [str(item) for item in asr_runtime_requirements() if not item.exists()]
    if missing:
        raise ASRServiceError("model_loading", f"ASR runtime is incomplete: {missing}")
    if not _INFERENCE_LOCK.acquire(blocking=False):
        raise ASRServiceError("server_busy", "Mega-ASR is already processing another request")
    converted_path: Path | None = None
    try:
        inference_path = path
        if path.suffix.lower() != ".wav":
            converted_path = _transcode_to_wav(path)
            inference_path = converted_path
        cache_dir = settings.mega_asr_numba_cache_dir.resolve()
        cache_dir.mkdir(parents=True, exist_ok=True)
        process_env = os.environ.copy()
        process_env["NUMBA_CACHE_DIR"] = str(cache_dir)
        if using_small_cpu_model():
            command = [
                str(settings.mega_asr_python),
                str(Path(__file__).with_name("asr_small_runner.py")),
                "--audio",
                str(inference_path.resolve()),
                "--model_path",
                str(settings.qwen_asr_small_model_dir),
                "--device_map",
                settings.mega_asr_device,
                "--max_new_tokens",
                str(settings.asr_max_new_tokens),
            ]
        else:
            command = [
                str(settings.mega_asr_python),
                "infer.py",
                "--audio",
                str(inference_path.resolve()),
                "--ckpt_dir",
                str(settings.mega_asr_ckpt_dir),
                "--device_map",
                settings.mega_asr_device,
            ]
        try:
            timeout_seconds = (
                settings.asr_small_timeout_seconds
                if using_small_cpu_model()
                else settings.mega_asr_timeout_seconds
            )
            completed = subprocess.run(
                command,
                cwd=settings.mega_asr_root,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False,
                env=process_env,
            )
        except subprocess.TimeoutExpired as exc:
            raise ASRServiceError("transcription_error", f"{settings.asr_model_mode} inference timed out") from exc
        output = "\n".join(part for part in (completed.stdout, completed.stderr) if part)
        if completed.returncode != 0:
            raise ASRServiceError(_error_code(output), output.strip()[-2000:])
        return _parse_result(completed.stdout)
    finally:
        if converted_path is not None:
            converted_path.unlink(missing_ok=True)
        _INFERENCE_LOCK.release()
