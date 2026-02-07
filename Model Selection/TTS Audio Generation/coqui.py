"""
coqui.py — Generate alternating-host TTS segments using Coqui XTTS v2

IMPORTANT:
XTTS needs *speaker reference audio* (a short WAV per voice).
Set VOICE1_WAV and VOICE2_WAV to your reference WAV paths.

Outputs:
- Segments: TTS Audio Generation/coqui_output/seg_000_host1.wav, ...
- Concat list: .../concat_list.txt
- Final: .../final.wav
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import List
import torch

# Allowlist XTTS config class for PyTorch 2.6+ weights_only loader
from TTS.tts.configs.xtts_config import XttsConfig

torch.serialization.add_safe_globals([XttsConfig])


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

# Provide short reference WAVs (3–15s is usually fine). Must exist.
VOICE1_WAV = r"host1.wav"
VOICE2_WAV = r"host2.wav"

LANGUAGE = "en"
MODEL_NAME = "tts_models/multilingual/multi-dataset/xtts_v2"  # Coqui TTS model id
# ------------------------------

BASE_DIR = Path(__file__).resolve().parent
OUT_DIR = BASE_DIR / "coqui_output"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def run_ffmpeg_concat(segments: List[Path], out_wav: Path) -> None:
    """
    Concatenate WAV segments with ffmpeg concat demuxer.
    Creates concat_list.txt in the same directory as out_wav.
    """
    concat_file = out_wav.parent / "concat_list.txt"
    with concat_file.open("w", encoding="utf-8") as f:
        for seg in segments:
            # ffmpeg concat demuxer requires: file 'path'
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
        "-c",
        "copy",
        str(out_wav),
    ]
    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError:
        raise RuntimeError(
            "ffmpeg not found on PATH. Install ffmpeg or add it to PATH."
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"ffmpeg concat failed: {e}")


def main() -> None:
    # Lazy import so the script fails fast if dependencies are missing
    from TTS.api import TTS  # pip install TTS

    v1 = Path(VOICE1_WAV)
    v2 = Path(VOICE2_WAV)
    if not v1.exists() or not v2.exists():
        raise FileNotFoundError(
            "XTTS requires two reference WAV files.\n"
            f"Missing:\n- {v1}\n- {v2}\n"
            "Set VOICE1_WAV and VOICE2_WAV to valid paths."
        )

    # Use GPU if available (Coqui TTS handles this internally); you can force CPU with:
    # os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
    tts = TTS(model_name=MODEL_NAME)

    segments: List[Path] = []
    for i, text in enumerate(CONVERSATION):
        speaker_wav = str(v1) if (i % 2 == 0) else str(v2)
        host = "host1" if (i % 2 == 0) else "host2"
        seg_path = OUT_DIR / f"seg_{i:03d}_{host}.wav"

        # XTTS synthesis
        tts.tts_to_file(
            text=text.strip(),
            file_path=str(seg_path),
            speaker_wav=speaker_wav,
            language=LANGUAGE,
        )
        print("Wrote:", seg_path)
        segments.append(seg_path)

    final_wav = OUT_DIR / "final.wav"
    run_ffmpeg_concat(segments, final_wav)
    print("Final written:", final_wav)


if __name__ == "__main__":
    main()
