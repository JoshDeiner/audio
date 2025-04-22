#!/usr/bin/env python3
"""Audio transcription module using faster-whisper.

This module provides functionality to record audio from a microphone
and transcribe it using the faster-whisper model.

It also supports transcribing existing audio files for testing and
development when recording is not possible.

The implementation follows a service-oriented architecture with clear
separation of concerns between audio recording, transcription processing,
and output management.
"""
import logging
import sys
from typing import List, Tuple, Union

from colorama import Fore, Style, init  # type: ignore
from dotenv import load_dotenv

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


def main() -> Union[Tuple[str, str], List[str], None]:
    """
    Execute the main transcription workflow based on command line arguments.

    Returns:
        Union[Tuple[str, str], List[str], None]:
            - Tuple: For recording mode, returns paths to audio and transcript files
            - List: For file or directory transcription, returns list of transcript texts

    Raises:
        SystemExit: If an error or user interruption occurs
    """
    try:
        args = parse_arguments()

        mode = (
            "file" if args.file else
            "dir" if args.dir else
            "record"
        )

        match mode:
            case "file":
                transcription_service = FileTranscriptionService()
                return [
                    transcription_service.transcribe_file(
                        args.file, args.model, args.language
                    )
                ]
            case "dir":
                transcription_service = FileTranscriptionService()
                return transcription_service.transcribe_directory(
                    args.dir, args.model, args.language
                )
            case "record":
                recording_service = ApplicationService()
                return recording_service.run(duration=args.duration)
            case _:
                print(f"\n{Fore.RED}Unknown mode: {mode}{Style.RESET_ALL}")
                logger.error(f"Unknown mode: {mode}")
                sys.exit(1)

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Process interrupted by user.{Style.RESET_ALL}")
        sys.exit(0)
    except (AudioServiceError, FileOperationError) as error:
        print(f"\n{Fore.RED}Error: {error}{Style.RESET_ALL}")
        logger.error(f"Application error: {error}")
        sys.exit(1)
    except Exception as error:
        print(f"\n{Fore.RED}Unexpected error: {error}{Style.RESET_ALL}")
        logger.error(f"Unexpected error: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
