#!/usr/bin/env python3
"""
Create Dummy WAV Files for Testing

This script generates dummy WAV files with sine waves at different frequencies
to test the audio transcription system without needing a microphone.
"""

import argparse
import os
from pathlib import Path

import numpy as np
import soundfile as sf


def create_sine_wave(duration=5.0, freq=440.0, sample_rate=16000):
    """
    Create a sine wave audio signal.

    Args:
        duration: Duration of the audio in seconds
        freq: Frequency of the sine wave in Hz
        sample_rate: Sample rate in Hz

    Returns:
        Numpy array containing the audio data
    """
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    audio = 0.5 * np.sin(2 * np.pi * freq * t)
    return audio


def create_dummy_wav(output_path, duration=5.0, freq=440.0, sample_rate=16000):
    """
    Create a dummy WAV file with a sine wave.

    Args:
        output_path: Path to save the WAV file
        duration: Duration of the audio in seconds
        freq: Frequency of the sine wave in Hz
        sample_rate: Sample rate in Hz
    """
    audio = create_sine_wave(duration, freq, sample_rate)
    sf.write(output_path, audio, sample_rate)
    print(f"Created dummy WAV file: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Create dummy WAV files for testing")
    parser.add_argument(
        "--output", "-o", default="input/dummy_sine.wav", help="Output file path"
    )
    parser.add_argument(
        "--duration", "-d", type=float, default=5.0, help="Duration in seconds"
    )
    parser.add_argument(
        "--frequency", "-f", type=float, default=440.0, help="Frequency in Hz"
    )
    parser.add_argument(
        "--sample-rate", "-sr", type=int, default=16000, help="Sample rate in Hz"
    )

    args = parser.parse_args()

    # Ensure the output directory exists
    output_path = Path(args.output)
    os.makedirs(output_path.parent, exist_ok=True)

    create_dummy_wav(args.output, args.duration, args.frequency, args.sample_rate)


if __name__ == "__main__":
    main()
