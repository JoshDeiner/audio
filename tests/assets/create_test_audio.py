"""Create test audio files for integration tests.

This script creates a simple audio file for testing the transcription pipeline.
"""

import argparse
import os
import struct
import wave

import numpy as np


def create_sine_wave(freq=440, duration=3, sample_rate=16000, amplitude=0.5):
    """Create a sine wave with the given parameters.

    Args:
        freq: Frequency in Hz
        duration: Duration in seconds
        sample_rate: Sample rate in Hz
        amplitude: Amplitude (0.0-1.0)

    Returns:
        numpy array of audio samples
    """
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    samples = amplitude * np.sin(2 * np.pi * freq * t)
    return samples


def create_test_audio(output_path, freq=440, duration=3):
    """Create a test audio file for testing.

    Args:
        output_path: Path to save the audio file
        freq: Frequency in Hz
        duration: Duration in seconds
    """
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Create a sine wave
    sample_rate = 16000  # 16kHz for Whisper
    audio_data = create_sine_wave(freq, duration, sample_rate)

    # Convert to int16
    audio_data = (audio_data * 32767).astype(np.int16)

    # Save to WAV file
    with wave.open(output_path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_data.tobytes())

    print(f"Created test audio file at {output_path}")
    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create test audio files")
    parser.add_argument(
        "--output",
        default="/home/jd01/audio/tests/assets/test_audio.wav",
        help="Output file path",
    )
    parser.add_argument(
        "--freq", type=int, default=440, help="Frequency in Hz"
    )
    parser.add_argument(
        "--duration", type=float, default=3.0, help="Duration in seconds"
    )

    args = parser.parse_args()
    create_test_audio(args.output, args.freq, args.duration)
