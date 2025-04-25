"""Utility for recording audio from microphone or generating dummy audio."""

import argparse
import os

import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write


def record_wav(filename="dummy_speech.wav", duration=5, samplerate=16000) -> None:
    """Record audio from microphone or generate dummy audio if microphone is not available.

    Args:
        filename: Path to save the WAV file
        duration: Duration of recording in seconds
        samplerate: Sample rate of the recording
    """
    print(f"Recording for {duration} seconds...")

    try:
        # Try to record from microphone
        audio = sd.rec(
            int(duration * samplerate),
            samplerate=samplerate,
            channels=1,
            dtype="int16",
        )
        sd.wait()  # Wait until recording is finished
    except Exception as e:
        # If recording fails (e.g., no microphone), generate dummy audio
        print(f"Recording failed: {e}")
        print("Generating dummy audio instead...")
        t = np.linspace(
            0, duration, int(samplerate * duration), endpoint=False
        )
        audio = np.sin(2 * np.pi * 440 * t).astype(np.int16) * 10000
        audio = audio.reshape(-1, 1)  # Reshape to match channels

    # Create the output directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)

    # Save the audio
    write(filename, samplerate, audio)
    print(f"Recording saved to: {filename}")

    return filename


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Record or generate dummy WAV file"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="dummy_speech.wav",
        help="Output file path (default: dummy_speech.wav)",
    )
    parser.add_argument(
        "--duration",
        "-d",
        type=int,
        default=5,
        help="Recording duration in seconds (default: 5)",
    )
    parser.add_argument(
        "--sample-rate",
        "-r",
        type=int,
        default=16000,
        help="Sample rate in Hz (default: 16000)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    record_wav(
        filename=args.output,
        duration=args.duration,
        samplerate=args.sample_rate,
    )
