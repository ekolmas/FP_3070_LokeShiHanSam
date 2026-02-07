import os
import time
import argparse
from pathlib import Path
from dotenv import load_dotenv
import torch
from huggingface_hub import login
from diffusers import DiffusionPipeline


def maybe_login():
    load_dotenv()
    token = os.environ.get("HF_TOKEN")
    if token:
        login(token=token)


def pick_device(device: str) -> str:
    if device != "auto":
        return device
    if torch.cuda.is_available():
        return "cuda"
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def main():
    parser = argparse.ArgumentParser(
        description="Generate an image with SDXL (stabilityai/stable-diffusion-xl-base-1.0)"
    )
    parser.add_argument(
        "--prompt", required=True, type=str, default="A beautiful landscape painting"
    )
    parser.add_argument("--negative", default="", type=str)
    parser.add_argument("--steps", default=30, type=int)
    parser.add_argument("--guidance", default=7.0, type=float)
    parser.add_argument("--width", default=1024, type=int)
    parser.add_argument("--height", default=1024, type=int)
    parser.add_argument("--seed", default=0, type=int)
    parser.add_argument("--outdir", default="outputs", type=str)
    parser.add_argument(
        "--device", choices=["auto", "cuda", "cpu", "mps"], default="auto"
    )
    parser.add_argument("--dtype", choices=["fp16", "bf16", "fp32"], default="fp16")
    args = parser.parse_args()

    maybe_login()
    device = pick_device(args.device)

    dtype_map = {"fp16": torch.float16, "bf16": torch.bfloat16, "fp32": torch.float32}
    dtype = dtype_map[args.dtype]

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    outpath = outdir / f"sdxl_{time.strftime('%Y%m%d_%H%M%S')}.png"

    pipe = DiffusionPipeline.from_pretrained(
        "stabilityai/stable-diffusion-xl-base-1.0",
        torch_dtype=dtype,
        use_safetensors=True,
        variant="fp16" if dtype in (torch.float16, torch.bfloat16) else None,
    ).to(device)

    generator = torch.Generator(
        device=device if device in ("cuda", "mps") else "cpu"
    ).manual_seed(args.seed)

    result = pipe(
        prompt=args.prompt,
        negative_prompt=args.negative if args.negative else None,
        num_inference_steps=args.steps,
        guidance_scale=args.guidance,
        width=args.width,
        height=args.height,
        generator=generator,
    )

    img = result.images[0]
    img.save(outpath)
    print(f"Saved: {outpath.resolve()}")


if __name__ == "__main__":
    main()
