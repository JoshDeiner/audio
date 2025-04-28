"""Main entry point for the audio package with async support.

This module provides the main function that parses command-line arguments
and runs the appropriate audio pipeline.

Author: Claude Code
Created: 2025-04-27
"""

import asyncio
import logging
from typing import Dict

from audio.audio_pipeline_controller_refactored import AudioPipelineController
from audio.utilities.argument_parser import ArgumentParser
from dependency_injection import container
from services.exceptions import AudioServiceError
from services.interfaces.audio_service_interface import IAudioRecordingService
from services.interfaces.configuration_manager_interface import (
    IConfigurationManager,
)
from services.interfaces.file_service_interface import IFileService
from services.interfaces.transcription_service_interface import (
    ITranscriptionService,
)
from services.service_provider import service_provider

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
        # Get services from the DI container via service provider
        config_manager = service_provider.get_config_manager()
        transcription_service = service_provider.get_transcription_service()
        file_service = service_provider.get_file_service()
        audio_service = service_provider.get_audio_recording_service()

        # Create controller with injected dependencies
        controller = AudioPipelineController(
            args,
            config_manager,
            transcription_service,
            file_service,
            audio_service,
        )

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
        # Get services from the DI container via service provider
        config_manager = service_provider.get_config_manager()
        transcription_service = service_provider.get_transcription_service()
        file_service = service_provider.get_file_service()
        audio_service = service_provider.get_audio_recording_service()

        # Create controller with injected dependencies
        controller = AudioPipelineController(
            args,
            config_manager,
            transcription_service,
            file_service,
            audio_service,
        )

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

        # Get services from the DI container via service provider
        config_manager = service_provider.get_config_manager()
        transcription_service = service_provider.get_transcription_service()
        file_service = service_provider.get_file_service()
        audio_service = service_provider.get_audio_recording_service()

        # Create controller with injected dependencies
        controller = AudioPipelineController(
            args,
            config_manager,
            transcription_service,
            file_service,
            audio_service,
        )

        await controller.handle_conversation_loop(max_turns=max_turns)
        print("\nConversation completed successfully.\n")
    except AudioServiceError as e:
        logger.error(f"Audio service error: {e}")
        print(f"Error: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        print(f"An unexpected error occurred: {e}")


async def main_async() -> None:
    """Run the audio application with async support."""
    # Initialize dependency container first
    service_provider.configure()

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
    finally:
        # Clean up any remaining resources
        try:
            service_provider.cleanup()
        except Exception as e:
            logger.warning(f"Error during cleanup: {e}")


if __name__ == "__main__":
    main()
