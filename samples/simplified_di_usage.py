"""Sample usage of the simplified DI approach.

This module demonstrates how to use the simplified dependency injection
approach for prototype development.
"""

import asyncio
from typing import Any, Dict

from audio.audio_pipeline_controller import AudioPipelineController
from library.bin.dependency_injection.app_services import AppServices
from services.file_service import FileService
from services.transcription_service import TranscriptionService


async def transcribe_audio_file(input_file: str) -> str:
    """Transcribe an audio file using the simplified DI approach.

    Args:
        input_file: Path to the audio file to transcribe

    Returns:
        The transcription result
    """
    # Initialize services with configuration
    config = {
        "WHISPER_MODEL": "tiny",
        "WHISPER_COMPUTE_TYPE": "int8",
        "WHISPER_DEVICE": "cpu",
    }
    services = AppServices(config)

    # Configure the pipeline
    pipeline_config: Dict[str, Any] = {
        "audio_path": input_file,
        "model": "tiny",
        "language": "en",
        "save_transcript": True,
    }

    # Create the pipeline controller with dependencies injected
    controller = AudioPipelineController(
        pipeline_config,
        services.config_manager,
        services.transcription_service,
        services.file_service,
        services.audio_service,
    )

    # Alternative way to create the controller using the factory method
    # controller = AudioPipelineController.from_services(pipeline_config, services)

    # Process the audio file
    transcription = await controller.handle_audio_in()
    print(f"Transcription: {transcription}")

    return transcription


async def demonstrate_manual_service_override() -> None:
    """Demonstrate how to override a service for testing or customization."""

    # Create a custom FileService implementation
    class CustomFileService(FileService):
        def validate_audio_file(self, file_path: str) -> bool:
            print(f"Custom validation for file: {file_path}")
            # Always return valid for testing
            return True

    # Create a custom TranscriptionService with a mock implementation
    class MockTranscriptionService(TranscriptionService):
        def transcribe_audio(
            self, audio_file_path: str, model_size=None, language=None
        ) -> str:
            return "This is a mock transcription for testing purposes."

    # Initialize services
    services = AppServices()

    # Override the services with our custom implementations
    services.register_instance(FileService, CustomFileService())
    services.register_instance(
        TranscriptionService, MockTranscriptionService()
    )

    # Configure the pipeline
    pipeline_config = {
        "audio_path": "dummy.wav",
        "save_transcript": False,
    }

    # Create the controller with the overridden services
    controller = AudioPipelineController.from_services(
        pipeline_config, services
    )

    # Process the audio file with mock services
    transcription = await controller.handle_audio_in()
    print(f"Mock transcription: {transcription}")


async def main() -> None:
    """Run the sample demonstration."""
    print("=== Simplified DI Demonstration ===")

    # Example 1: Transcribe an audio file
    print("\n1. Simple transcription:")
    try:
        await transcribe_audio_file("input/sample.wav")
    except Exception as e:
        print(f"Error: {e}")

    # Example 2: Manual service override
    print("\n2. Service override for testing:")
    await demonstrate_manual_service_override()


if __name__ == "__main__":
    asyncio.run(main())
