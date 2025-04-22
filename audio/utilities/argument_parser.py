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


def add_test_file_arguments(parser: argparse.ArgumentParser) -> None:
    """Add test file generation arguments to the parser.

    Args:
        parser: The argument parser to add arguments to
    """
    group = parser.add_argument_group("Test file generation")
    group.add_argument(
        "--create-dummy",
        "-c",
        action="store_true",
        help="Create a dummy WAV file for testing",
    )
    group.add_argument(
        "--dummy-text",
        metavar="TEXT",
        help="Text to use for speech synthesis (requires gtts and librosa)",
    )


def add_seed_arguments(parser: argparse.ArgumentParser) -> None:
    """Add seed functionality arguments to the parser.

    Args:
        parser: The argument parser to add arguments to
    """
    group = parser.add_argument_group("Seed functionality")
    group.add_argument(
        "--seed",
        action="store_true",
        help="Use seed functionality to generate test audio files",
    )
    group.add_argument(
        "--seed-type",
        choices=["sine", "speech", "multi-language", "test-suite"],
        default="sine",
        help="Type of seed audio to generate (default: sine)",
    )
    group.add_argument(
        "--output",
        "-o",
        metavar="PATH",
        help="Output path for generated audio file",
    )
    group.add_argument(
        "--frequency",
        type=float,
        default=440.0,
        help="Frequency in Hz for sine wave (default: 440.0)",
    )
    group.add_argument(
        "--sample-rate",
        type=int,
        default=16000,
        help="Sample rate in Hz (default: 16000)",
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
    add_test_file_arguments(parser)
    add_seed_arguments(parser)

    return parser.parse_args()
