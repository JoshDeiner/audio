#!/usr/bin/env python3
"""Argument parsing utilities for the audio package.

This module provides functions to configure command-line arguments for
the audio transcription tool.
"""
import argparse


def add_mode_arguments(parser: argparse.ArgumentParser) -> None:
    """Add mode selection arguments to the parser.

    Args:
        parser: The argument parser to add arguments to
    """
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--record",
        "-r",
        action="store_true",
        help="Record audio from microphone (default mode)",
    )
    mode_group.add_argument(
        "--file", "-f", metavar="FILE", help="Transcribe a specific audio file"
    )
    mode_group.add_argument(
        "--dir",
        "-d",
        metavar="DIR",
        help="Transcribe all WAV files in a directory",
    )
    mode_group.add_argument(
        "--audio-out",
        "-ao",
        action="store_true",
        help="Enable audio output mode for text-to-speech conversion",
    )
    mode_group.add_argument(
        "--audio-in",
        "-ai",
        action="store_true",
        help="Enable audio input mode for speech-to-text conversion",
    )


def add_recording_arguments(parser: argparse.ArgumentParser) -> None:
    """Add recording-related arguments to the parser.

    Args:
        parser: The argument parser to add arguments to
    """
    group = parser.add_argument_group("Recording options")
    group.add_argument(
        "--duration",
        "-t",
        type=int,
        default=5,
        help="Recording duration in seconds (default: 5)",
    )


def add_transcription_arguments(parser: argparse.ArgumentParser) -> None:
    """Add transcription-related arguments to the parser.

    Args:
        parser: The argument parser to add arguments to
    """
    group = parser.add_argument_group("Transcription options")
    group.add_argument(
        "--model",
        "-m",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model size (default: from .env or 'tiny')",
    )
    group.add_argument(
        "--language",
        "-l",
        help="Language code to use (e.g., 'en' for English). Skips language detection.",
    )


def add_audio_out_arguments(parser: argparse.ArgumentParser) -> None:
    """Add audio-out related arguments to the parser.

    Args:
        parser: The argument parser to add arguments to
    """
    group = parser.add_argument_group("Audio output options")
    group.add_argument(
        "--data-source",
        type=str,
        help="Optional text to synthesize into audio (used in audio-out mode)",
    )
    group.add_argument(
        "--output",
        type=str,
        help="Optional output path for synthesized audio file or transcription text file",
    )
    group.add_argument(
        "--play",
        action="store_true",
        help="Play the synthesized audio after generation (audio-out mode only)",
    )
    group.add_argument(
        "--return-text-output",
        action="store_true",
        help="Return synthesized text instead of audio path (for testing/debugging)",
    )


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments.

    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Audio transcription tool using faster-whisper"
    )

    add_mode_arguments(parser)
    add_recording_arguments(parser)
    add_transcription_arguments(parser)
    add_audio_out_arguments(parser)

    return parser.parse_args()
