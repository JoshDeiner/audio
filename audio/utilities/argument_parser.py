#!/usr/bin/env python3
"""Argument parsing utilities for the audio package.

This module provides an ArgumentParser class that configures and parses
command-line arguments for the audio application, supporting both synchronous
and asynchronous operation modes.

Author: Claude Code
Created: 2025-04-27
"""
import argparse
from typing import Any, Dict, Optional, Tuple


class ArgumentParser:
    """Parser for command-line arguments used by the audio application.

    This class encapsulates all argument parsing logic for the application,
    including support for audio-in, audio-out, and conversation modes.
    """

    def __init__(self) -> None:
        """Initialize the argument parser."""
        self.parser = argparse.ArgumentParser(
            description="Audio transcription and synthesis tool",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )

        # Add subparsers for different commands
        self.subparsers = self.parser.add_subparsers(
            dest="command", help="Command to execute", required=True
        )

        # Set up command parsers
        self._setup_audio_in_parser()
        self._setup_audio_out_parser()
        self._setup_conversation_parser()

    def _setup_audio_in_parser(self) -> None:
        """Set up the parser for the audio-in command."""
        parser = self.subparsers.add_parser(
            "audio-in", help="Record and transcribe audio"
        )

        # Input source options
        source_group = parser.add_mutually_exclusive_group()
        source_group.add_argument(
            "--record",
            "-r",
            action="store_true",
            help="Record audio from microphone (default mode)",
        )
        source_group.add_argument(
            "--file",
            "-f",
            metavar="FILE",
            help="Transcribe a specific audio file",
            dest="audio_path",
        )

        # Recording options
        parser.add_argument(
            "--duration",
            "-t",
            type=int,
            default=5,
            help="Recording duration in seconds (default: 5)",
        )

        # Transcription options
        parser.add_argument(
            "--model",
            "-m",
            choices=["tiny", "base", "small", "medium", "large"],
            help="Whisper model size (default: from .env or 'tiny')",
        )
        parser.add_argument(
            "--language",
            "-l",
            help="Language code to use (e.g., 'en' for English). Skips language detection.",
        )

        # Output options
        parser.add_argument(
            "--output",
            "-o",
            dest="output_path",
            help="Optional output path for transcription text file",
        )
        parser.add_argument(
            "--save-transcript",
            action="store_true",
            help="Save transcription to a text file",
        )

    def _setup_audio_out_parser(self) -> None:
        """Set up the parser for the audio-out command."""
        parser = self.subparsers.add_parser(
            "audio-out", help="Convert text to speech"
        )

        # Input source
        parser.add_argument(
            "--data-source",
            required=True,
            help="Text or file path to synthesize into audio",
        )

        # Output options
        parser.add_argument(
            "--output",
            "-o",
            dest="output_path",
            help="Optional output path for synthesized audio file",
        )
        parser.add_argument(
            "--play",
            action="store_true",
            default=True,
            help="Play the synthesized audio after generation",
        )
        parser.add_argument(
            "--no-play",
            action="store_false",
            dest="play_audio",
            help="Disable audio playback",
        )
        parser.add_argument(
            "--return-text-output",
            action="store_true",
            help="Return synthesized text instead of audio path (for testing/debugging)",
        )

    def _setup_conversation_parser(self) -> None:
        """Set up the parser for the conversation command."""
        parser = self.subparsers.add_parser(
            "conversation", help="Start an interactive conversation loop"
        )

        # Conversation options
        parser.add_argument(
            "--turns",
            type=int,
            default=5,
            help="Maximum number of conversation turns",
        )
        parser.add_argument(
            "--duration",
            "-t",
            type=int,
            default=5,
            help="Recording duration per turn in seconds",
        )
        parser.add_argument(
            "--model",
            "-m",
            choices=["tiny", "base", "small", "medium", "large"],
            help="Whisper model size for transcription",
        )
        parser.add_argument(
            "--language",
            "-l",
            help="Language code to use for conversation",
        )

    def parse_arguments(self) -> Tuple[Dict[str, Any], str]:
        """Parse command line arguments.

        Returns:
            Tuple[Dict[str, Any], str]: A tuple containing:
                - Dictionary of parsed arguments
                - Command name as a string

        Example:
            ```python
            parser = ArgumentParser()
            args, command = parser.parse_arguments()
            if command == "audio-in":
                # Handle audio input mode
            elif command == "audio-out":
                # Handle audio output mode
            ```
        """
        args = self.parser.parse_args()

        # Convert Namespace to dictionary
        args_dict = vars(args)

        # Extract command and remove from dictionary
        command = args_dict.pop("command")

        # Return args dictionary and command
        return args_dict, command
