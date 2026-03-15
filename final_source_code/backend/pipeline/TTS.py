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
# Voice presets for suno bark
voice_1 = "v2/en_speaker_6"
voice_2 = "v2/en_speaker_9"
# Model name for suno bark
suno_model = "suno/bark"


# Function purpose: remove unwanted text from the conversation before audio is generated
# using regex to remove common speaker labels and extra whitespace for easier TTS processing
def clean_tts_text(text):
    clean_text_re = re.compile(
        r"^\s*(host\s*\d+|host|guest|speaker\s*\d+|narrator)\s*:\s*", re.IGNORECASE
    )
    text = text.strip()
    text = clean_text_re.sub("", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


# Function purpose: Create a txt file containing lists of segments (each speaker's turn) and run ffmpeg concat to produce final output wav file
def concatenate_ffmpeg(
    segment_list,
    output_wav_path,
    runner: Callable = subprocess.run,
):
    # Ensure output directory exists
    output_wav_path = Path(output_wav_path)
    output_wav_path.parent.mkdir(parents=True, exist_ok=True)
    # Create a text file listing all segment paths for ffmpeg concat
    concatenated_file = output_wav_path.parent / "concatenated_list.txt"

    # read concat list file
    with concatenated_file.open("w", encoding="utf-8") as f:
        # for each segment, write a line to the concat list file in the format expected by ffmpeg
        # format looks like 'file 'path/to/segment.wav'
        for segment in segment_list:
            segment = Path(segment).resolve()
            f.write(f"file '{segment.as_posix()}'\n")

    # ffmpeg command to concatenate the segments into a single wav file
    command = [
        "ffmpeg",
        # -y to overwrite output file if exists
        "-y",
        # hide banner and log level for clean output unless error
        "-hide_banner",
        "-loglevel",
        # only show error
        "error",
        # -f concat for concat demuxer
        "-f",
        "concat",
        # -safe 0 allows absolute paths in the concat list file
        "-safe",
        "0",
        # -i for input concat list file
        "-i",
        str(concatenated_file),
        # -c for codec copy to preserve original audio quality
        "-c",
        "copy",
        str(output_wav_path),
    ]

    # Run the ffmpeg command
    try:
        runner(command, check=True)
    # ffmpeg not found in PATH
    except FileNotFoundError:
        raise RuntimeError("There is no ffmpeg in the PATH")
    # ffmpeg concat failed
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Concatenation process failed: {e}")

    return output_wav_path


# Function purpose: Full TTS process. Generate suno bark tts segments and concatenate into a final output named after article id
def generate_audio(
    article_id,
    conversation,
    output_directory="tts_output",
    voice_1=voice_1,
    voice_2=voice_2,
    model=suno_model,
):
    # Validate required parameters and conversation format
    if not article_id:
        raise ValueError("article_id is required")
    if not isinstance(conversation, list) or not all(
        isinstance(x, str) for x in conversation
    ):
        raise ValueError("conversation must be a list containing strings")
    if len(conversation) == 0:
        raise ValueError("conversation cannot be empty")

    # Create output directory for the article
    output_directory = Path(output_directory)
    article_folder_directory = output_directory / str(article_id)
    article_folder_directory.mkdir(parents=True, exist_ok=True)

    # Load the TTS model and processor
    processor = AutoProcessor.from_pretrained(model)
    bark = BarkModel.from_pretrained(model)

    # Move model to GPU if available for faster inference
    device = "cuda" if torch.cuda.is_available() else "cpu"
    bark = bark.to(device)

    # get sample rate from model configuration for correct sample rate when writing wav files
    sample_rate = bark.generation_config.sample_rate

    segments: List[Path] = []
    # Iterate through the conversation, alternating between the two voices for each speaker's turn
    for i, text in enumerate(conversation):
        is_host1_turn = i % 2 == 0
        if is_host1_turn:
            preset = voice_1
            host = "host1"
        else:
            preset = voice_2
            host = "host2"

        # Generate unique segment file name with segment and host index
        seg_path = article_folder_directory / f"segment_{i:03d}_{host}.wav"
        cleaned_text = clean_tts_text(text)

        # Prepare input for TTS model using processor
        inputs = processor(
            text=cleaned_text.strip(), voice_preset=preset, return_tensors="pt"
        )
        # move input tensors to the same device as the model
        inputs = {k: v.to(device) for k, v in inputs.items()}

        # generate audio without gradient tracking
        with torch.no_grad():
            audio = bark.generate(**inputs)

        # Move audio tensor to CPU and convert to numpy array for writing to wav file
        audio = audio.cpu().numpy().squeeze()
        wav_write(str(seg_path), sample_rate, (audio * 32767).astype("int16"))
        segments.append(seg_path)

    # After generating all segments, concatenant into a final wav file named after the article id
    final_wav = article_folder_directory / f"{article_id}.wav"
    concatenate_ffmpeg(segments, final_wav)

    return final_wav
