"""Integration tests for audio pipeline controller."""
import os
import subprocess
import sys
from pathlib import Path

import pytest

@pytest.mark.integration
def test_audio_in_pipeline_prints_transcription(tmp_path):
    """Test audio-in pipeline transcribes and prints results."""
    # Create a dummy audio file
    audio_file = tmp_path / "test.wav"
    
    # Using the script in dummy/ to create a real audio file
    dummy_script = Path(__file__).parent.parent.parent / "dummy" / "record_dummy_wav.py"
    subprocess.run(
        [sys.executable, str(dummy_script), "--output", str(audio_file), "--duration", "1"],
        check=True
    )
    
    # Set output directory
    output_dir = tmp_path / "output"
    os.environ["AUDIO_OUTPUT_DIR"] = str(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    
    # Run the audio-in pipeline
    result = subprocess.run(
        [sys.executable, "-m", "audio", "--file", str(audio_file)],
        capture_output=True,
        text=True
    )
    
    # Check output
    assert "Transcription" in result.stdout, f"Expected 'Transcription' in output, got: {result.stdout}"
    
    # Check transcript file is created
    transcript_files = list(output_dir.glob("*.txt"))
    assert transcript_files, f"No transcript files found in {output_dir}"

@pytest.mark.integration
def test_audio_out_pipeline_uses_default_text(tmp_path):
    """Test audio-out pipeline with default text."""
    # Set output directory
    output_dir = tmp_path / "output"
    os.environ["AUDIO_OUTPUT_DIR"] = str(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    
    # Set a specific output file
    output_file = tmp_path / "output.wav"
    
    # Run the audio-out pipeline
    result = subprocess.run(
        [sys.executable, "-m", "audio", "--output", str(output_file)],
        capture_output=True,
        text=True
    )
    
    # Check output file exists
    assert output_file.exists(), f"Output file not created: {output_file}"
    assert output_file.stat().st_size > 0, "Output file is empty"

@pytest.mark.integration
def test_audio_out_pipeline_uses_custom_text_and_output(tmp_path):
    """Test audio-out pipeline with custom text and output path."""
    # Set output directory
    output_dir = tmp_path / "output"
    os.environ["AUDIO_OUTPUT_DIR"] = str(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    
    # Set a specific output file
    output_file = tmp_path / "custom.wav"
    
    # Run the audio-out pipeline with custom text
    result = subprocess.run(
        [
            sys.executable, 
            "-m", "audio", 
            "--text", "Hello from test", 
            "--output", str(output_file)
        ],
        capture_output=True,
        text=True
    )
    
    # Check output file exists
    assert output_file.exists(), f"Output file not created: {output_file}"
    assert output_file.stat().st_size > 0, "Output file is empty"

@pytest.mark.integration
def test_audio_out_pipeline_with_play_flag(tmp_path):
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
            "-m", "audio", 
            "--output", str(output_file),
            "--play"
        ],
        capture_output=True,
        text=True
    )
    
    # Check output file exists
    assert output_file.exists(), f"Output file not created: {output_file}"
    # Check for playback reference in output
    assert "Playing audio" in result.stdout, "No mention of audio playback in output"