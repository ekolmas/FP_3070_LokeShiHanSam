# Text to speech using suno bark

from __future__ import annotations
import os
import subprocess
import wave
from pathlib import Path
from typing import Callable, List, Optional
import torch
from transformers import AutoProcessor, BarkModel
from scipy.io.wavfile import write as wav_write
import re

# Congfigurations for suno bark
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
voice_1 = "v2/en_speaker_6"
voice_2 = "v2/en_speaker_9"
suno_model = "suno/bark"


# Function purpose: remove unwanted text from the conversation before audio is generated
def clean_tts_text(text):
    clean_text_re = re.compile(
        r"^\s*(host\s*\d+|host|guest|speaker\s*\d+|narrator)\s*:\s*", re.IGNORECASE
    )
    text = text.strip()
    text = clean_text_re.sub("", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


# creating silent wav for the gaps between speeches
def create_silent_wav(path="tts_output/silence.wav", seconds=0.1, sample_rate=24000):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    number_of_frames = int(seconds * sample_rate)
    silent_frames = b"\x00\x00" * number_of_frames

    with wave.open(str(path), "wb") as wavfile:
        wavfile.setnchannels(1)
        wavfile.setsampwidth(2)
        wavfile.setframerate(sample_rate)
        wavfile.writeframes(silent_frames)

    return path


# Function purpose: Create a txt file containing lists of segments and run ffmpeg concat to produce final output wav file
def concatenate_ffmpeg(
    segment_list,
    output_wav_path,
    runner: Callable = subprocess.run,
):
    output_wav_path = Path(output_wav_path)
    output_wav_path.parent.mkdir(parents=True, exist_ok=True)
    concatenated_file = output_wav_path.parent / "concatenated_list.txt"

    with concatenated_file.open("w", encoding="utf-8") as f:
        for segment in segment_list:
            segment = Path(segment).resolve()
            # ffmpeg concat demuxer expects forward slashes; resolve() gives absolute
            f.write(f"file '{segment.as_posix()}'\n")

    command = [
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
        str(concatenated_file),
        "-c",
        "copy",
        str(output_wav_path),
    ]

    try:
        runner(command, check=True)
    except FileNotFoundError:
        raise RuntimeError("There is no ffmpeg in the PATH")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Concatenation process failed: {e}")

    return output_wav_path


# Function purpose: Generate suno bark tts segments and concatenate into a final output named after article id
def generate_audio(
    article_id,
    conversation,
    output_directory="tts_output",
    voice_1=voice_1,
    voice_2=voice_2,
    model=suno_model,
):
    if not article_id:
        raise ValueError("article_id is required")
    if not isinstance(conversation, list) or not all(
        isinstance(x, str) for x in conversation
    ):
        raise ValueError("conversation must be a list containing strings")
    if len(conversation) == 0:
        raise ValueError("conversation cannot be empty")

    output_directory = Path(output_directory)
    article_folder_directory = output_directory / str(article_id)
    article_folder_directory.mkdir(parents=True, exist_ok=True)

    processor = AutoProcessor.from_pretrained(model)
    bark = BarkModel.from_pretrained(model)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    bark = bark.to(device)

    sample_rate = bark.generation_config.sample_rate

    segments: List[Path] = []
    for i, text in enumerate(conversation):
        is_host1_turn = i % 2 == 0
        if is_host1_turn:
            preset = voice_1
            host = "host1"
        else:
            preset = voice_2
            host = "host2"

        seg_path = article_folder_directory / f"segment_{i:03d}_{host}.wav"
        cleaned_text = clean_tts_text(text)

        inputs = processor(
            text=cleaned_text.strip(), voice_preset=preset, return_tensors="pt"
        )
        inputs = {k: v.to(device) for k, v in inputs.items()}

        with torch.no_grad():
            audio = bark.generate(**inputs)

        audio = audio.cpu().numpy().squeeze()
        wav_write(str(seg_path), sample_rate, (audio * 32767).astype("int16"))
        segments.append(seg_path)

    final_wav = article_folder_directory / f"{article_id}.wav"
    concatenate_ffmpeg(segments, final_wav)

    return final_wav
