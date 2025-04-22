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
import os
import sys
import argparse
from typing import List, Optional, Tuple, Union

from colorama import Fore, Style, init  # type: ignore
from dotenv import load_dotenv
from utilities.argument_parser import parse_arguments
from dummy import create_dummy_file, run_seed_functionality

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
    """Execute the main transcription workflow based on command line arguments.

    Returns:
        Union[Tuple[str, str], List[str], None]:
            - For recording: Paths to the audio file and transcript file
            - For file transcription: List of transcription texts
            - None if creating dummy files only

    Raises:
        SystemExit: If an error occurs during execution
    """
    try:
        args = parse_arguments()

        # Handle seed functionality if requested
        if args.seed:
            output_path = run_seed_functionality(args)
            if not args.file and not args.dir and output_path:
                # If only creating seed file and not transcribing, exit after creation
                if os.path.isdir(output_path):
                    return None
                # Otherwise set the file to transcribe
                args.file = output_path

        # Create dummy file if requested
        elif args.create_dummy:
            dummy_path = create_dummy_file(args.dummy_text)
            if not args.file and not args.dir:
                # If only creating dummy file, exit after creation
                return None
            # Otherwise, set the file to transcribe to the dummy file
            args.file = dummy_path

        # Determine mode and execute appropriate workflow
        if args.file:
            # File transcription mode
            file_service = FileTranscriptionService()
            return [
                file_service.transcribe_file(
                    args.file, args.model, args.language
                )
            ]

        elif args.dir:
            # Directory transcription mode
            file_service = FileTranscriptionService()
            return file_service.transcribe_directory(
                args.dir, args.model, args.language
            )

        else:
            # Default: recording mode
            app_service = ApplicationService()
            return app_service.run(duration=args.duration)

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Process interrupted by user.{Style.RESET_ALL}")
        sys.exit(0)
    except (AudioServiceError, FileOperationError) as e:
        print(f"\n{Fore.RED}Error: {e}{Style.RESET_ALL}")
        logger.error(f"Application error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Fore.RED}Unexpected error: {e}{Style.RESET_ALL}")
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
