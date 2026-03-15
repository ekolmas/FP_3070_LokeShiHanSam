# Unit testing for Text to speech
import os
import json
import types
import pytest
import wave
from pathlib import Path
from pipeline.TTS import generate_audio


# First test: generate segmented audio and final concatenated audio using Bark TTS
# successfully passed
@pytest.mark.slow
def test_generate_audio_bark_creates_segments_and_final():
    conversation = [
        "Hi, this is the first speaker.",
        "Hi, this is the second speaker.",
        "This is the third speaker.",
    ]

    article_id = "test_article_001"
    output_dir = Path("tts_output")

    final_wav = generate_audio(
        article_id=article_id, conversation=conversation, output_directory=output_dir
    )

    # final file exists
    assert final_wav.exists()
    assert final_wav.name == f"{article_id}.wav"

    # segments exist
    seg0 = output_dir / article_id / "segment_000_host1.wav"
    seg1 = output_dir / article_id / "segment_001_host2.wav"
    seg2 = output_dir / article_id / "segment_002_host1.wav"

    assert seg0.exists()
    assert seg1.exists()
    assert seg2.exists()

    # concat list exists
    concat_list = output_dir / article_id / "concatenated_list.txt"
    assert concat_list.exists()
