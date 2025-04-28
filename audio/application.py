"""Application entry point with dependency injection support.

This module provides the main application class that bootstraps the DI container
and serves as the composition root for the application.
"""

import asyncio
import logging
from typing import Any, Dict, Optional

from audio.audio_pipeline_controller import AudioPipelineController
from audio.utilities.argument_parser import ArgumentParser
from dependency_injection.bootstrap import bootstrap_application
from dependency_injection.container import (
    DIContainer,
    ServiceLifetime,
)
from services.exceptions import AudioServiceError
from services.interfaces.audio_service_interface import IAudioRecordingService
from services.interfaces.configuration_manager_interface import (
    IConfigurationManager,
)
from services.interfaces.file_service_interface import IFileService
from services.interfaces.transcription_service_interface import (
    ITranscriptionService,
)
from services.service_provider import ServiceProvider

logger = logging.getLogger(__name__)


class Application:
    """Main application class with dependency injection support.

    This class serves as the composition root for the application,
    bootstrapping the DI container and coordinating service usage.
    """

    def __init__(self) -> None:
        """Initialize the application."""
        self.container = DIContainer()
        self.service_provider: Optional[ServiceProvider] = None

    async def initialize(
        self, config: Optional[Dict[str, Any]] = None
    ) -> None:
        """Initialize the application asynchronously.

        Args:
            config: Optional application configuration
        """
        # Bootstrap the DI container
        from dependency_injection.bootstrap import (
            bootstrap_application as bootstrap,
        )

        bootstrap(self.container, config)

        # Create a service provider
        self.service_provider = ServiceProvider(self.container)

        logger.info("Application initialized")

    async def run(self, args: Optional[Dict[str, Any]] = None) -> int:
        """Run the application with the given arguments.

        Args:
            args: Optional command line arguments

        Returns:
            Exit code (0 for success, non-zero for error)
        """
        if not self.service_provider:
            await self.initialize()

        try:
            # Parse command line arguments
            parser = ArgumentParser()
            parsed_args, command = parser.parse_arguments(args)

            # Run the appropriate command
            if command == "audio-in":
                await self._handle_audio_in(parsed_args)
            elif command == "audio-out":
                await self._handle_audio_out(parsed_args)
            elif command == "conversation":
                await self._handle_conversation(parsed_args)
            else:
                print("Invalid command. Use --help for usage information.")
                return 1

            return 0
        except Exception as e:
            logger.exception(f"Error running application: {e}")
            print(f"An error occurred: {e}")
            return 1

    async def _handle_audio_in(self, args: Dict[str, Any]) -> None:
        """Handle the audio-in command.

        Args:
            args: Command line arguments
        """
        if not self.service_provider:
            raise RuntimeError("Application not initialized")

        try:
            # Get required services from the DI container
            config_manager = self.service_provider.get_config_manager()
            transcription_service = (
                self.service_provider.get_transcription_service()
            )
            file_service = self.service_provider.get_file_service()
            audio_service = self.service_provider.get_audio_recording_service()

            # Create the controller with dependencies injected
            controller = AudioPipelineController(
                args,
                config_manager,
                transcription_service,
                file_service,
                audio_service,
            )

            # Run the audio input pipeline
            transcription = await controller.handle_audio_in()
            print(f"\nTranscription result: {transcription}\n")
        except AudioServiceError as e:
            logger.error(f"Audio service error: {e}")
            print(f"Error: {e}")
            raise

    async def _handle_audio_out(self, args: Dict[str, Any]) -> None:
        """Handle the audio-out command.

        Args:
            args: Command line arguments
        """
        if not self.service_provider:
            raise RuntimeError("Application not initialized")

        try:
            # Get required services from the DI container
            config_manager = self.service_provider.get_config_manager()
            transcription_service = (
                self.service_provider.get_transcription_service()
            )
            file_service = self.service_provider.get_file_service()
            audio_service = self.service_provider.get_audio_recording_service()

            # Create the controller with dependencies injected
            controller = AudioPipelineController(
                args,
                config_manager,
                transcription_service,
                file_service,
                audio_service,
            )

            # Run the audio output pipeline
            audio_path = await controller.handle_audio_out()
            print(f"\nAudio output saved to: {audio_path}\n")
        except AudioServiceError as e:
            logger.error(f"Audio service error: {e}")
            print(f"Error: {e}")
            raise

    async def _handle_conversation(self, args: Dict[str, Any]) -> None:
        """Handle the conversation command.

        Args:
            args: Command line arguments
        """
        if not self.service_provider:
            raise RuntimeError("Application not initialized")

        try:
            # Parse max turns
            max_turns = int(args.get("turns", "5"))

            # Get required services from the DI container
            config_manager = self.service_provider.get_config_manager()
            transcription_service = (
                self.service_provider.get_transcription_service()
            )
            file_service = self.service_provider.get_file_service()
            audio_service = self.service_provider.get_audio_recording_service()

            # Create the controller with dependencies injected
            controller = AudioPipelineController(
                args,
                config_manager,
                transcription_service,
                file_service,
                audio_service,
            )

            # Run the conversation loop
            await controller.handle_conversation_loop(max_turns=max_turns)
            print("\nConversation completed successfully.\n")
        except AudioServiceError as e:
            logger.error(f"Audio service error: {e}")
            print(f"Error: {e}")
            raise

    def shutdown(self) -> None:
        """Shut down the application and release resources."""
        logger.info("Shutting down application")
        # Add any cleanup code here


def main() -> int:
    """Main entry point for the application.

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        # Create and run the application
        app = Application()
        return asyncio.run(app.run())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        return 130  # Standard exit code for SIGINT
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        print(f"A fatal error occurred: {e}")
        return 1
    finally:
        # Ensure cleanup
        try:
            app = Application()
            app.shutdown()
        except Exception as e:
            logger.warning(f"Error during shutdown: {e}")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Run the application
    exit_code = main()
    exit(exit_code)
