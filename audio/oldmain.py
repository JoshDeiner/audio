#!/usr/bin/env python3
"""Audio processing module for transcription and synthesis.

This module provides functionality to:
1. Record audio from a microphone and transcribe it
2. Transcribe existing audio files
3. Synthesize text into speech and play it back

It follows a service-oriented architecture with clear separation of concerns
between audio recording, transcription processing, synthesis, and output management.
"""
import argparse
import logging
import sys
from typing import List, Optional, Tuple, Union

from colorama import Fore, Style, init
from dotenv import load_dotenv

from audio.audio_pipeline_controller import AudioPipelineController
from audio.utilities.argument_parser import parse_arguments
from services.application_service import ApplicationService
from services.exceptions import AudioServiceError, FileOperationError
from services.file_transcription_service import FileTranscriptionService

# Load environment variables from .env file
load_dotenv()

# Initialize colorama with strip=False for compatibility with Docker/TTY
init(strip=False)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def _determine_mode(args: argparse.Namespace) -> Optional[str]:
    """Determine the operation mode based on arguments.

    Args:
        args: Parsed command line arguments

    Returns:
        Optional[str]: The operation mode or None if no mode specified
    """
    if args.audio_in:
        return "audio_in"
    elif args.audio_out:
        return "audio_out"
    elif args.file:
        return "file"
    elif args.dir:
        return "dir"
    elif args.record:
        return "record"
    else:
        return None


def main() -> Union[Tuple[str, str], List[str], str, None]:
    """
    Execute the main workflow based on command line arguments.

    Returns:
        Union[Tuple[str, str], List[str], str, None]:
            - Tuple: For recording mode, returns paths to audio and transcript files
            - List: For file or directory transcription, returns list of transcript texts
            - str: For audio synthesis, returns path to output audio file
            - None: If an error occurs or process is interrupted

    Raises:
        SystemExit: If an error or user interruption occurs

    Example:
        ```python
        # When called from command line
        if __name__ == "__main__":
            main()

        # When imported as module
        from audio.__main__ import main
        result = main()
        ```
    """
    try:
        # Parse arguments
        args = parse_arguments()

        # Determine operation mode using helper function
        mode = _determine_mode(args)

        # Guard clause for unknown mode
        if not mode:
            print(
                f"\n{Fore.RED}No operation mode specified. Use -h for help.{Style.RESET_ALL}"
            )
            logger.error("No operation mode specified")
            sys.exit(1)

        # Handle each mode
        match mode:
            case "file":
                config = {
                    "audio_path": args.file,
                    "model": args.model,
                    "language": args.language,
                    "save_transcript": True,
                }
                controller = AudioPipelineController(config)
                return controller.handle_audio_in()

            case "audio_in":
                config = {
                    "audio_path": args.file,  # Will be None if not provided
                    "model": args.model,
                    "language": args.language,
                    "duration": args.duration,
                    "output_path": args.output,  # Output path for transcript
                    "save_transcript": True,
                }
                controller = AudioPipelineController(config)
                return controller.handle_audio_in()

            case "dir":
                transcription_service = FileTranscriptionService()
                return transcription_service.transcribe_directory(
                    args.dir, args.model, args.language
                )

            case "record":
                recording_service = ApplicationService()
                return recording_service.run(duration=args.duration)

            case "audio_out":
                config = {
                    "data_source": args.data_source,
                    "output_path": args.output,
                    "play_audio": args.play if args.play is not None else True,
                    "return_text_output": args.return_text_output,
                }
                controller = AudioPipelineController(config)
                result = controller.handle_audio_out()
                if args.return_text_output:
                    print(f"Synthesized text output: {result}")
                return result

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Process interrupted by user.{Style.RESET_ALL}")
        sys.exit(0)

    except AudioServiceError as error:
        # Enhanced error reporting with error codes
        error_code = getattr(error, "error_code", "UNKNOWN")
        print(
            f"\n{Fore.RED}Audio Service Error [{error_code}]: {error}{Style.RESET_ALL}"
        )
        logger.error(f"Audio Service Error [{error_code}]: {error}")
        sys.exit(1)

    except FileOperationError as error:
        # Enhanced error reporting with error codes
        error_code = getattr(error, "error_code", "UNKNOWN")
        details = getattr(error, "details", {})
        detail_str = f" - Details: {details}" if details else ""

        print(
            f"\n{Fore.RED}File Operation Error [{error_code}]: {error}{Style.RESET_ALL}"
        )
        logger.error(
            f"File Operation Error [{error_code}]: {error}{detail_str}"
        )
        sys.exit(1)

    except Exception as error:
        print(f"\n{Fore.RED}Unexpected error: {error}{Style.RESET_ALL}")
        logger.error(
            f"Unexpected error: {error}", exc_info=True
        )  # Include stack trace
        sys.exit(1)

    # This will never execute due to sys.exit() calls above,
    # but it helps satisfy the type checker
    return None


if __name__ == "__main__":
    main()
