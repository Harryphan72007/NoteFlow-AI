from __future__ import annotations

import argparse
import time
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the lightweight Qwen3-ASR CPU model")
    parser.add_argument("--audio", required=True)
    parser.add_argument("--model_path", required=True)
    parser.add_argument("--device_map", default="cpu")
    parser.add_argument("--max_new_tokens", type=int, default=256)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    import torch
    from qwen_asr import Qwen3ASRModel

    started = time.perf_counter()
    dtype = torch.float32 if args.device_map == "cpu" else torch.bfloat16
    model = Qwen3ASRModel.from_pretrained(
        str(Path(args.model_path).resolve()),
        dtype=dtype,
        device_map=args.device_map,
        max_inference_batch_size=1,
        max_new_tokens=args.max_new_tokens,
    )
    loaded = time.perf_counter()
    results = model.transcribe(audio=str(Path(args.audio).resolve()))
    finished = time.perf_counter()
    texts = [
        str(getattr(result, "text", result)).strip()
        for result in (results if isinstance(results, list) else [results])
    ]
    print(
        {
            "text": texts,
            "model": "Qwen3-ASR-0.6B",
            "model_family": "Qwen3-ASR",
            "route_source": "small_base",
            "use_lora": False,
            "mega_asr_features": False,
        }
    )
    print(
        f"[timing] load={loaded-started:.2f}s  infer={finished-loaded:.2f}s  "
        f"total={finished-started:.2f}s"
    )


if __name__ == "__main__":
    main()
