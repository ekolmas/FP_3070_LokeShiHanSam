import asyncio
import subprocess
from pathlib import Path
import edge_tts

voices = [
    "en-US-JennyNeural",
    "en-US-GuyNeural"
]

# function to speak a single line
async def speak_one_line(text, voice, out_path):
    tts = edge_tts.Communicate(text=text, voice=voice)
    await tts.save(str(out_path))

# function to generate audio by looping through dialogue and stitching segments
async def run_tts(dialogue, output_directory):
    output_directory.mkdir(exist_ok=True)
    final_output = output_directory / "final_podcast.mp3"

    all_speech_files = []

    for i, line in enumerate(dialogue):
        output = output_directory / f"seg_{i+1:02d}.mp3"
        await speak_one_line(line, voices[i % len(voices)], output)
        all_speech_files.append(output)

    # Create concatenated list for ffmpeg to stitch together
    # Cannot use all_speech_files directly because ffmpeg takes in a txt file
    concat_file = output_directory / "concat.txt"
    with open(concat_file, "w", encoding="utf-8") as f:
        for seg in all_speech_files:
            f.write(f"file '{seg.resolve()}'\n")

    # Stitch using ffmpeg
    subprocess.run([
        "ffmpeg",
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_file),
        "-c", "copy",
        str(final_output)
    ], check=True)

    return final_output

# main function to be called in pipeline.py
def generate_podcast_audio(dialogue, output_directory='tts_out'):
    output_directory = Path(output_directory)
    final_output_path = asyncio.run(run_tts(dialogue, output_directory))
    return str(final_output_path.resolve())