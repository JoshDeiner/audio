#!/usr/bin/env python3
"""Audio processing module for transcription and synthesis.

This module provides functionality to:
1. Record audio from a microphone and transcribe it 
2. Transcribe existing audio files
3. Synthesize text into speech and play it back

It follows a service-oriented architecture with clear separation of concerns
between audio recording, transcription processing, synthesis, and output management.
"""
import logging
import sys
from typing import List, Tuple, Union

from colorama import Fore, Style, init  # type: ignore
from dotenv import load_dotenv

from audio.utilities.argument_parser import parse_arguments
from audio.audio_pipeline_controller import AudioPipelineController
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


def main() -> Union[Tuple[str, str], List[str], str, None]:
    """
    Execute the main workflow based on command line arguments.

    Returns:
        Union[Tuple[str, str], List[str], str, None]:
            - Tuple: For recording mode, returns paths to audio and transcript files
            - List: For file or directory transcription, returns list of transcript texts
            - str: For audio synthesis, returns path to output audio file

    Raises:
        SystemExit: If an error or user interruption occurs
    """
    try:
        args = parse_arguments()

        # Check for audio-out mode
        if args.text is not None or args.output is not None or args.play:
            # Audio output pipeline
            config = {
                "text": args.text,
                "output_path": args.output,
                "play_audio": args.play if args.play is not None else True,
            }
            controller = AudioPipelineController(config)
            return controller.handle_audio_out()
        
        # Otherwise, use existing audio-in modes
        mode = (
            "file" if args.file else
            "dir" if args.dir else
            "record"
        )

        match mode:
            case "file":
                config = {
                    "audio_path": args.file,
                    "model": args.model,
                    "language": args.language,
                    "save_transcript": True
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