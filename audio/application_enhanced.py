"""Enhanced application entry point with comprehensive dependency injection support.

This module provides the main application class that bootstraps the DI container
and serves as the composition root for the application, with additional services.
"""

import asyncio
import logging
from typing import Any, Dict, Optional, Sequence

from audio.audio_pipeline_controller_refactored import AudioPipelineController
from audio.utilities.argument_parser_di import IArgumentParser
from dependency_injection.bootstrap_updated import bootstrap_application, cleanup_container
from dependency_injection.container_enhanced import DIContainer, ServiceLifetime
from services.exceptions import AudioServiceError
from services.interfaces.application_service_interface import IApplicationService
from services.interfaces.audio_playback_service_interface import IAudioPlaybackService
from services.interfaces.audio_service_interface import IAudioRecordingService
from services.interfaces.configuration_manager_interface import IConfigurationManager
from services.interfaces.file_service_interface import IFileService
from services.interfaces.file_transcription_service_interface import IFileTranscriptionService
from services.interfaces.text_to_speech_service_interface import ITextToSpeechService
from services.interfaces.transcription_service_interface import ITranscriptionService
from services.service_provider_enhanced import ServiceProvider

logger = logging.getLogger(__name__)


class Application:
    """Enhanced application class with comprehensive DI support.
    
    This class serves as the composition root for the application,
    bootstrapping the DI container and coordinating service usage.
    """
    
    def __init__(self) -> None:
        """Initialize the application."""
        self.container = DIContainer()
        self.service_provider: Optional[ServiceProvider] = None
        
    async def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the application asynchronously.
        
        Args:
            config: Optional application configuration
        """
        # Bootstrap the container with all services
        bootstrap_application(self.container, config)
        
        # Create a service provider
        self.service_provider = ServiceProvider(self.container)
        
        logger.info("Application initialized with all services")
        
    async def run(self, args: Optional[Sequence[str]] = None) -> int:
        """Run the application with the given arguments.
        
        Args:
            args: Optional command line arguments
            
        Returns:
            Exit code (0 for success, non-zero for error)
        """
        if not self.service_provider:
            await self.initialize()
            
        try:
            # Get argument parser from container
            parser = self.service_provider.get(IArgumentParser)
            
            # Parse command line arguments
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
            transcription_service = self.service_provider.get_transcription_service()
            file_service = self.service_provider.get_file_service()
            audio_service = self.service_provider.get_audio_recording_service()
            
            # Create the controller with dependencies injected
            controller = AudioPipelineController(
                args,
                config_manager,
                transcription_service,
                file_service,
                audio_service
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
            transcription_service = self.service_provider.get_transcription_service()
            file_service = self.service_provider.get_file_service()
            audio_service = self.service_provider.get_audio_recording_service()
            
            # Additional services specifically for audio-out
            text_to_speech_service = self.service_provider.get(ITextToSpeechService)
            audio_playback_service = self.service_provider.get(IAudioPlaybackService)
            
            # Create the controller with dependencies injected
            controller = AudioPipelineController(
                args,
                config_manager,
                transcription_service,
                file_service,
                audio_service
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
            transcription_service = self.service_provider.get_transcription_service()
            file_service = self.service_provider.get_file_service()
            audio_service = self.service_provider.get_audio_recording_service()
            
            # Create the controller with dependencies injected
            controller = AudioPipelineController(
                args,
                config_manager,
                transcription_service,
                file_service,
                audio_service
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
        
        # Clean up container resources
        if self.container:
            cleanup_container(self.container)


def main() -> int:
    """Main entry point for the application.
    
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    
    app = Application()
    
    try:
        # Create and run the application
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
            app.shutdown()
        except Exception as e:
            logger.warning(f"Error during shutdown: {e}")


if __name__ == "__main__":
    # Run the application
    exit_code = main()
    exit(exit_code)