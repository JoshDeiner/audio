"""Main entry point for the audio package with async support.

This module provides the main function that parses command-line arguments
and runs the appropriate audio pipeline.

Author: Claude Code
Created: 2025-04-27
"""

import asyncio
import logging
from typing import Dict, List, Optional

from audio.refactored_pipeline_controller import AsyncAudioPipelineController
from audio.utilities.argument_parser import ArgumentParser
from services.exceptions import AudioServiceError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def handle_audio_in_command(args: Dict[str, str]) -> None:
    """Handle the audio-in command asynchronously.

    Args:
        args: Command-line arguments
    """
    try:
        controller = AsyncAudioPipelineController(args)
        transcription = await controller.handle_audio_in()
        print(f"\nTranscription result: {transcription}\n")
    except AudioServiceError as e:
        logger.error(f"Audio service error: {e}")
        print(f"Error: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        print(f"An unexpected error occurred: {e}")


async def handle_audio_out_command(args: Dict[str, str]) -> None:
    """Handle the audio-out command asynchronously.

    Args:
        args: Command-line arguments
    """
    try:
        controller = AsyncAudioPipelineController(args)
        audio_path = await controller.handle_audio_out()
        print(f"\nAudio output saved to: {audio_path}\n")
    except AudioServiceError as e:
        logger.error(f"Audio service error: {e}")
        print(f"Error: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        print(f"An unexpected error occurred: {e}")


async def handle_conversation_command(args: Dict[str, str]) -> None:
    """Handle the conversation command asynchronously.

    Args:
        args: Command-line arguments
    """
    try:
        max_turns = int(args.get("turns", "5"))
        controller = AsyncAudioPipelineController(args)
        await controller.handle_conversation_loop(max_turns=max_turns)
        print("\nConversation completed successfully.\n")
    except AudioServiceError as e:
        logger.error(f"Audio service error: {e}")
        print(f"Error: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        print(f"An unexpected error occurred: {e}")


async def main_async() -> None:
    """Main function to run the audio application with async support."""
    parser = ArgumentParser()
    args, command = parser.parse_arguments()

    if command == "audio-in":
        await handle_audio_in_command(args)
    elif command == "audio-out":
        await handle_audio_out_command(args)
    elif command == "conversation":
        await handle_conversation_command(args)
    else:
        print("Invalid command. Use --help for usage information.")


def main() -> None:
    """Entry point for the audio application that runs the async main function."""
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        print(f"A fatal error occurred: {e}")


if __name__ == "__main__":
    main()
