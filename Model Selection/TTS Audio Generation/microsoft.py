"""
microsoft.py — Generate alternating-host TTS segments using Microsoft SpeechT5 TTS

What it does
- Takes a conversation list like ["Host1 line", "Host2 line", "Host1 line", ...]
- Alternates between 2 different voices (Host1/Host2)
- Writes segment WAVs to: TTS Audio Generation/microsoft_output/
- Creates a final concatenated WAV (ffmpeg) in the same folder

Why this version works (your earlier error)
- Newer `datasets` versions no longer support dataset scripts, and
  "Matthijs/cmu-arctic-xvectors" uses a dataset script + a zip file.
- This script DOES NOT use `datasets`.
- It downloads `spkrec-xvect.zip` from the repo, extracts it, and builds
  speaker embeddings from the .npy files.

Requirements (install in the SAME env you run this with)
  pip install transformers torch scipy numpy huggingface_hub

Also requires ffmpeg on PATH for final concatenation.
"""

from __future__ import annotations

import os
import subprocess
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
from huggingface_hub import hf_hub_download

# ---- Fix common Windows OpenMP conflict ----
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

# --------- EDIT THESE ---------
CONVERSATION: List[str] = [
    "Hey everyone and welcome to Tech Talk Today! I'm Alex.",
    "And I'm Jamie. Today we're diving into something really exciting in the world of artificial intelligence - AI agents that can actually play games with us like human friends.",
    "That's right! We're talking about Altera, a new startup that just raised $9 million in seed funding to develop exactly these kinds of AI companions.",
    "Nine million is quite an investment! Who are their backers?",
    "The round was co-led by First Spark Ventures, which is Eric Schmidt's deep-tech fund, and Patron, a seed-stage fund co-founded by Riot Games alumni. They had previously raised $2 million in pre-seed funding back in January.",
    "Impressive backers indeed. So what exactly is Altera building?",
    'Their first product is an AI agent that can play Minecraft with you, "just like a friend." They\'re developing AI agents with "social-emotional intelligence" that can interact naturally with players and make their own decisions in-game.',
    "That sounds different from typical game AI or NPCs. How does it work exactly?",
    "Unlike traditional NPCs that follow scripts, these agents have the freedom to make their own decisions. In demos, they've shown the AI refusing to fight at first but eventually defending itself when provoked. It's designed to be a companion rather than an assistant that just follows commands.",
    "I'm curious about the practical applications. Is this just about gaming, or is there a bigger vision here?",
    'Right now they\'re starting with gaming - specifically Minecraft - but the long-term vision is much bigger. The company wants to create "multi-agent worlds" and eventually expand to digital humans with physical forms.',
    "Physical robots? That's quite a leap from Minecraft mods! Who's leading this ambitious project?",
    'The company is helmed by Robert Yang, a neuroscientist and former MIT professor. Yang and his co-founders actually stepped away from their applied research lab at MIT to focus on developing these AI agents, or "AI buddies" as he calls them.',
    "A neuroscientist leading an AI company - that's an interesting background. What's his motivation?",
    'Yang has stated that it\'s been his life goal as a neuroscientist to "go all the way and build a digital human being." However, he emphasizes they have a "solidly pro-human framework" and are building agents that will enhance humanity, not replace it.',
    "That's reassuring. What's Altera's business model? They're not focused on enterprise applications, which seems to be where most AI development is heading these days.",
    "That's one of the most interesting aspects - they're specifically targeting consumer applications rather than enterprise AI. Yang believes gaming offers faster iteration, better data collection, and eager users. For now, they're not even talking about monetization strategies.",
    "How advanced are these AI agents technically? Can they really play like humans?",
    "According to the article, they're capable of performing all kinds of human-like activities in Minecraft - building, crafting, farming, trading, mining, attacking, equipping items, chatting and moving around. They're designed to feel like playing with real friends, including the trolling and competition.",
    "That sounds both impressive and potentially frustrating depending on your playing style! Where are they in development?",
    "They're currently testing the model with 750 Minecraft players and plan to officially launch later this summer. The app will be free to download but will include some paid features.",
    "Beyond Minecraft, what's their roadmap look like?",
    'Minecraft is just the starting point. They plan to expand to other games like Stardew Valley and eventually integrate their technology with game engine SDKs for broader developer use. The key is that their agents "execute an action as code," meaning they can potentially play any game without needing material customization.',
    "With backing from high-profile investors including Benchmark partner Mitch Lasky and Valorant co-founder Stephen Lim, there's clearly significant confidence in their vision.",
    'Absolutely. Aaron Sisto from First Spark Ventures mentioned that today\'s AI lacks critical traits like empathy, embodiment, and personal goals, which prevent it from forming real connections with people. They believe Altera is building "radically new types of AI agents that are fun, unique, and persistent across platforms."',
    "It's fascinating to think about where this could go - from gaming companions to potentially AI friends or assistants in various aspects of our digital lives.",
    "Exactly! And we might see this future sooner than we think, with Altera planning to launch their Minecraft AI agent this summer.",
    "Well, this is certainly something we'll be keeping an eye on. Thanks for breaking down this exciting AI development with us today, Alex.",
    "Thanks for having me, Jamie. Listeners, what do you think about AI gaming companions? Let us know your thoughts!",
]

# Option A: pick by index (recommended if you just want 2 different voices quickly).
# This index refers to a sorted list of speaker IDs we detect from the zip.
SPEAKER_INDEX_1 = 0
SPEAKER_INDEX_2 = 1

# Option B (optional): pick explicit speaker IDs (overrides indices if set)
# Typical CMU Arctic IDs include: bdl, slt, jmk, awb, rms, clb, ksp
SPEAKER_ID_1: Optional[str] = "bdl"  # e.g. "bdl"
SPEAKER_ID_2: Optional[str] = "slt"  # e.g. "slt"

PROCESSOR_ID = "microsoft/speecht5_tts"
MODEL_ID = "microsoft/speecht5_tts"
VOCODER_ID = "microsoft/speecht5_hifigan"
XVECTORS_DATASET = "Matthijs/cmu-arctic-xvectors"
# ------------------------------

BASE_DIR = Path(__file__).resolve().parent
OUT_DIR = BASE_DIR / "microsoft_output"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def run_ffmpeg_concat(segments: List[Path], out_wav: Path) -> None:
    """
    Concatenate WAV segments using ffmpeg concat demuxer.
    """
    concat_file = out_wav.parent / "concat_list.txt"
    with concat_file.open("w", encoding="utf-8") as f:
        for seg in segments:
            f.write(f"file '{seg.as_posix()}'\n")

    cmd = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat_file),
        # Re-encode to be safe across WAV headers
        "-ar",
        "16000",
        "-ac",
        "1",
        str(out_wav),
    ]
    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError as e:
        raise RuntimeError(
            "ffmpeg not found on PATH. Install ffmpeg or add it to PATH."
        ) from e
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"ffmpeg concat failed: {e}") from e


def _infer_speaker_id_from_path(path: Path) -> Optional[str]:
    """
    Best-effort inference of speaker ID from filename/path tokens.
    CMU Arctic commonly uses tokens like bdl/slt/jmk/awb/rms/clb/ksp.
    """
    known = {"bdl", "slt", "jmk", "awb", "rms", "clb", "ksp"}
    tokens = []
    # tokens from filename
    tokens += path.stem.lower().replace("-", "_").split("_")
    # tokens from parent folders
    for p in path.parents:
        tokens += p.name.lower().replace("-", "_").split("_")

    for t in tokens:
        if t in known:
            return t
    return None


def _download_and_extract_xvectors(repo_id: str, cache_dir: Path) -> Path:
    """
    Download spkrec-xvect.zip from the HF dataset repo and extract it.
    Returns the extraction directory path.
    """
    cache_dir.mkdir(parents=True, exist_ok=True)

    zip_path = hf_hub_download(
        repo_id=repo_id,
        filename="spkrec-xvect.zip",
        repo_type="dataset",
        cache_dir=str(cache_dir),
    )

    extract_dir = cache_dir / "spkrec-xvect_extracted"
    if not extract_dir.exists():
        extract_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(str(extract_dir))

    return extract_dir


def load_speaker_xvectors(repo_id: str, cache_dir: Path) -> Dict[str, np.ndarray]:
    """
    Builds a dict of speaker_id -> mean pooled xvector (float32, shape (512,))
    from the extracted .npy files.

    If speaker inference fails for some files, those files are ignored.
    """
    extract_dir = _download_and_extract_xvectors(repo_id, cache_dir)
    npy_files = list(extract_dir.rglob("*.npy"))
    if not npy_files:
        raise RuntimeError(f"No .npy files found after extracting: {extract_dir}")

    by_spk: Dict[str, List[np.ndarray]] = {}
    ignored = 0

    for f in npy_files:
        spk = _infer_speaker_id_from_path(f)
        if spk is None:
            ignored += 1
            continue
        vec = np.load(f).astype("float32").reshape(-1)
        # Most xvectors are 512-d; keep anything reasonable
        if vec.size < 64:
            ignored += 1
            continue
        by_spk.setdefault(spk, []).append(vec)

    if not by_spk:
        raise RuntimeError(
            "Could not infer any speaker IDs from extracted xvectors. "
            "Zip layout may have changed."
        )

    spk_means: Dict[str, np.ndarray] = {}
    for spk, vecs in by_spk.items():
        spk_means[spk] = np.mean(np.stack(vecs, axis=0), axis=0).astype("float32")

    # Helpful info printed once
    speakers_sorted = sorted(spk_means.keys())
    print("Detected speaker IDs:", speakers_sorted)
    if ignored:
        print(
            f"Note: ignored {ignored} xvector files that didn't match known speaker IDs."
        )

    return spk_means


def pick_speakers(
    spk_means: Dict[str, np.ndarray],
    idx1: int,
    idx2: int,
    sid1: Optional[str],
    sid2: Optional[str],
) -> Tuple[str, str, np.ndarray, np.ndarray]:
    """
    Choose two speakers either by explicit ID (if provided) or by index.
    """
    speakers_sorted = sorted(spk_means.keys())

    # If explicit IDs provided, they win
    if sid1 is not None and sid2 is not None:
        if sid1 not in spk_means or sid2 not in spk_means:
            raise RuntimeError(
                f"Requested speaker IDs not available. "
                f"Available: {speakers_sorted}. Requested: {sid1}, {sid2}"
            )
        return sid1, sid2, spk_means[sid1], spk_means[sid2]

    # Otherwise pick by index
    if (
        idx1 < 0
        or idx2 < 0
        or idx1 >= len(speakers_sorted)
        or idx2 >= len(speakers_sorted)
    ):
        raise IndexError(
            f"Speaker index out of range. Have {len(speakers_sorted)} speakers: {speakers_sorted}. "
            f"Got idx1={idx1}, idx2={idx2}"
        )

    s1 = speakers_sorted[idx1]
    s2 = speakers_sorted[idx2]
    if s1 == s2:
        raise ValueError(
            "Speaker 1 and Speaker 2 resolved to the same ID. Choose different indices/IDs."
        )
    return s1, s2, spk_means[s1], spk_means[s2]


def main() -> None:
    import torch
    from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
    from scipy.io.wavfile import write as wav_write

    device = "cuda" if torch.cuda.is_available() else "cpu"

    processor = SpeechT5Processor.from_pretrained(PROCESSOR_ID)
    model = SpeechT5ForTextToSpeech.from_pretrained(MODEL_ID).to(device)
    vocoder = SpeechT5HifiGan.from_pretrained(VOCODER_ID).to(device)

    # Load speaker embeddings from zip (no datasets)
    cache_dir = OUT_DIR / "_hf_cache"
    spk_means = load_speaker_xvectors(XVECTORS_DATASET, cache_dir)

    sid1, sid2, vec1, vec2 = pick_speakers(
        spk_means,
        SPEAKER_INDEX_1,
        SPEAKER_INDEX_2,
        SPEAKER_ID_1,
        SPEAKER_ID_2,
    )
    print(f"Using speakers: Host1={sid1}, Host2={sid2}")

    spk1 = torch.tensor(vec1).unsqueeze(0).to(device)
    spk2 = torch.tensor(vec2).unsqueeze(0).to(device)

    segments: List[Path] = []
    for i, text in enumerate(CONVERSATION):
        speaker = spk1 if (i % 2 == 0) else spk2
        host = "host1" if (i % 2 == 0) else "host2"
        seg_path = OUT_DIR / f"seg_{i:03d}_{host}.wav"

        inputs = processor(text=text.strip(), return_tensors="pt")
        input_ids = inputs["input_ids"].to(device)

        with torch.no_grad():
            speech = model.generate_speech(
                input_ids,
                speaker_embeddings=speaker,
                vocoder=vocoder,
            )

        audio = speech.detach().cpu().numpy()
        sample_rate = 16000  # SpeechT5 output is 16kHz
        wav_write(str(seg_path), sample_rate, (audio * 32767).astype("int16"))

        print("Wrote:", seg_path)
        segments.append(seg_path)

    final_wav = OUT_DIR / "final.wav"
    run_ffmpeg_concat(segments, final_wav)
    print("Final written:", final_wav)


if __name__ == "__main__":
    main()
