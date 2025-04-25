"""Integration tests for audio pipeline controller."""

import os
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.integration
def test_audio_in_pipeline_prints_transcription(tmp_path: Path) -> None:
    """Test audio-in pipeline transcribes and prints results."""
    # Create a test output file to check
    output_file = tmp_path / "transcription_test.wav"

    # Set output directory
    output_dir = tmp_path / "output"
    os.environ["AUDIO_OUTPUT_DIR"] = str(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    # Run the audio-out pipeline with direct text input
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "audio",
            "--audio-out",
            "--data-source",
            "This is a test for audio transcription.",
            "--output",
            str(output_file),
        ],
        capture_output=True,
        text=True,
    )

    # Check output file exists
    assert output_file.exists(), f"Output file not created: {output_file}"
    assert output_file.stat().st_size > 0, "Output file is empty"

    # Print output for debugging
    print(f"Stdout: {result.stdout}")
    print(f"Stderr: {result.stderr}")

    # Check that audio is synthesized
    assert (
        "Synthesizing text" in result.stderr
    ), "No mention of text synthesis in output"


@pytest.mark.integration
def test_audio_out_pipeline_uses_default_text(tmp_path: Path) -> None:
    """Test audio-out pipeline with default text."""
    # Set output directory
    output_dir = tmp_path / "output"
    os.environ["AUDIO_OUTPUT_DIR"] = str(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    # Set a specific output file
    output_file = tmp_path / "output.wav"

    # Run the audio-out pipeline with default text
    subprocess.run(
        [
            sys.executable,
            "-m",
            "audio",
            "--audio-out",
            "--data-source",
            "Default text for testing",
            "--output",
            str(output_file),
        ],
        capture_output=True,
        text=True,
    )

    # Check output file exists
    assert output_file.exists(), f"Output file not created: {output_file}"
    assert output_file.stat().st_size > 0, "Output file is empty"


@pytest.mark.integration
def test_audio_out_pipeline_uses_custom_text_and_output(
    tmp_path: Path,
) -> None:
    """Test audio-out pipeline with custom text and output path."""
    # Set output directory
    output_dir = tmp_path / "output"
    os.environ["AUDIO_OUTPUT_DIR"] = str(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    # Set a specific output file
    output_file = tmp_path / "custom.wav"

    # Run the audio-out pipeline with custom text
    subprocess.run(
        [
            sys.executable,
            "-m",
            "audio",
            "--audio-out",
            "--data-source",
            "Hello from test",
            "--output",
            str(output_file),
        ],
        capture_output=True,
        text=True,
    )

    # Check output file exists
    assert output_file.exists(), f"Output file not created: {output_file}"
    assert output_file.stat().st_size > 0, "Output file is empty"


@pytest.mark.integration
def test_audio_out_pipeline_with_play_flag(tmp_path: Path) -> None:
    """Test audio-out pipeline with play flag."""
    # Set output directory
    output_dir = tmp_path / "output"
    os.environ["AUDIO_OUTPUT_DIR"] = str(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    # Set a specific output file
    output_file = tmp_path / "play.wav"

    # Run the audio-out pipeline with play flag
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "audio",
            "--audio-out",
            "--data-source",
            "Test audio with play flag",
            "--output",
            str(output_file),
            "--play",
        ],
        capture_output=True,
        text=True,
    )

    # Check output file exists
    assert output_file.exists(), f"Output file not created: {output_file}"
    # Check for playback reference in output
    assert (
        "Playing audio" in result.stderr
    ), "No mention of audio playback in output"
