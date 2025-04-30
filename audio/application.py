"""Application entry point with simplified dependency injection support.

This module provides the main application class that uses the simplified DI approach
and serves as the composition root for the application.
"""

import asyncio
import logging
from typing import Any, Dict, Optional

from audio.audio_pipeline_controller import AudioPipelineController
from audio.utilities.argument_parser import ArgumentParser
from library.bin.dependency_injection.app_services import AppServices
from services.exceptions import AudioServiceError

logger = logging.getLogger(__name__)


class Application:
    """Main application class with simplified dependency injection support.

    This class serves as the composition root for the application,
    using the simplified DI container for service management.
    """

    def __init__(self) -> None:
        """Initialize the application."""
        self.services: Optional[AppServices] = None

    async def initialize(
        self, config: Optional[Dict[str, Any]] = None
    ) -> None:
        """Initialize the application asynchronously.

        Args:
            config: Optional application configuration
        """
        # Initialize services with configuration
        self.services = AppServices(config)
        logger.info("Application initialized with simplified DI")

    async def run(self, args: Optional[Dict[str, Any]] = None) -> int:
        """Run the application with the given arguments.

        Args:
            args: Optional command line arguments

        Returns:
            Exit code (0 for success, non-zero for error)
        """
        if not self.services:
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
            elif command == "state-machine":
                await self._handle_state_machine(parsed_args)
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
        if not self.services:
            raise RuntimeError("Application not initialized")

        try:
            # Create the controller with dependencies injected
            controller = AudioPipelineController(
                args,
                self.services.config_manager,
                self.services.transcription_service,
                self.services.file_service,
                self.services.audio_service,
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
        if not self.services:
            raise RuntimeError("Application not initialized")

        try:
            # Create the controller with dependencies injected
            controller = AudioPipelineController(
                args,
                self.services.config_manager,
                self.services.transcription_service,
                self.services.file_service,
                self.services.audio_service,
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
        if not self.services:
            raise RuntimeError("Application not initialized")

        try:
            # Parse max turns
            max_turns = int(args.get("turns", "5"))

            # Create the controller with dependencies injected
            controller = AudioPipelineController(
                args,
                self.services.config_manager,
                self.services.transcription_service,
                self.services.file_service,
                self.services.audio_service,
            )

            # Run the conversation loop
            await controller.handle_conversation_loop(max_turns=max_turns)
            print("\nConversation completed successfully.\n")
        except AudioServiceError as e:
            logger.error(f"Audio service error: {e}")
            print(f"Error: {e}")
            raise
            
    async def _handle_state_machine(self, args: Dict[str, Any]) -> None:
        """Handle the state-machine command.

        Args:
            args: Command line arguments
        """
        if not self.services:
            raise RuntimeError("Application not initialized")

        try:
            # Import here to avoid circular imports
            from audio.async_state_machine import AsyncAudioStateMachine
            import os
            
            # Ensure required environment variables are set
            input_dir = self.services.config_manager.get("AUDIO_INPUT_DIR")
            if not input_dir:
                input_dir = os.path.join(os.getcwd(), "input")
                os.makedirs(input_dir, exist_ok=True)
                os.environ["AUDIO_INPUT_DIR"] = input_dir
                self.services.config_manager.set("AUDIO_INPUT_DIR", input_dir)
                logger.info(f"Set AUDIO_INPUT_DIR: {input_dir}")
            
            output_dir = self.services.config_manager.get("AUDIO_OUTPUT_DIR")
            if not output_dir:
                output_dir = os.path.join(os.getcwd(), "output")
                os.makedirs(output_dir, exist_ok=True)
                os.environ["AUDIO_OUTPUT_DIR"] = output_dir
                self.services.config_manager.set("AUDIO_OUTPUT_DIR", output_dir)
                logger.info(f"Set AUDIO_OUTPUT_DIR: {output_dir}")
            
            # Parse cycles and validate
            try:
                cycles = int(args.get("cycles", "2"))
                if cycles <= 0:
                    logger.warning(f"Invalid cycles value: {cycles}, must be > 0. Using default of 2.")
                    cycles = 2
                if cycles % 2 != 0:
                    original_cycles = cycles
                    cycles = cycles + (cycles % 2)
                    logger.info(f"Adjusted cycles from {original_cycles} to {cycles} to ensure even number")
                    print(f"Note: Adjusted requested {original_cycles} cycles to {cycles} for balanced listen/speak operation")
            except ValueError:
                logger.warning("Invalid cycles parameter, using default of 2")
                cycles = 2
            
            # Create the state machine with dependencies injected
            state_machine = AsyncAudioStateMachine(
                args,
                self.services.audio_service,
                self.services.transcription_service,
                self.services.config_manager,
                cycles=cycles
            )
            
            # Run the state machine
            print(f"\nStarting async state machine with {cycles} cycles...\n")
            await state_machine.run()
            print("\nState machine completed successfully.\n")
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
