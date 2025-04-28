"""Asynchronous audio pipeline controller for the audio package.

This module provides the controller that orchestrates the audio processing
pipelines for both input (recording/transcription) and output (synthesis/playback)
using asyncio for improved concurrency and responsiveness.

Author: Claude Code
Created: 2025-04-27
"""

import asyncio
import logging
import os
import time
from typing import Any, Dict, List, Optional

from dependency_injection.app_services import AppServices
from services.audio_playback_service import AudioPlaybackService
from services.exceptions import (
    AudioRecordingError,
    AudioServiceError,
    FileOperationError,
    TranscriptionError,
)
from services.interfaces.audio_service_interface import IAudioRecordingService
from services.interfaces.configuration_manager_interface import (
    IConfigurationManager,
)
from services.interfaces.file_service_interface import IFileService
from services.interfaces.transcription_service_interface import (
    ITranscriptionService,
)
from services.text_to_speech_service import TextToSpeechService

logger = logging.getLogger(__name__)


class AudioPipelineController:
    """Asynchronous controller for audio processing pipelines.

    This controller coordinates the various services required for audio
    processing, including recording, transcription, and synthesis using
    asyncio for improved concurrency.

    Attributes:
        config: Configuration dictionary with pipeline options
        transcription_service: Service for audio transcription
        file_service: Service for file operations
    """

    def __init__(
        self,
        config: Dict[str, Any],
        config_manager: IConfigurationManager,
        transcription_service: ITranscriptionService,
        file_service: IFileService,
        audio_service: IAudioRecordingService,
    ) -> None:
        """Initialize the controller with configuration and services.

        Args:
            config: Configuration dictionary with pipeline options
            config_manager: Configuration manager for application settings
            transcription_service: Service for audio transcription
            file_service: Service for file operations
            audio_service: Service for audio recording

        Example:
            ```python
            # Using the simplified AppServices container
            from dependency_injection.app_services import AppServices

            services = AppServices()
            config = {
                "model": "small",
                "language": "en",
                "duration": 10
            }
            controller = AudioPipelineController(
                config,
                services.config_manager,
                services.transcription_service,
                services.file_service,
                services.audio_service
            )

            # Alternative simplified constructor
            controller = AudioPipelineController.from_services(config, services)
            ```
        """
        self.config = config
        self.config_manager = config_manager
        self.transcription_service = transcription_service
        self.file_service = file_service
        self.audio_service = audio_service

        # Ensure directories exist
        self._ensure_directories()

    @classmethod
    def from_services(
        cls, config: Dict[str, Any], services: AppServices
    ) -> "AudioPipelineController":
        """Create a controller using the AppServices container.

        Args:
            config: Configuration dictionary with pipeline options
            services: AppServices container with all required services

        Returns:
            An initialized AudioPipelineController instance
        """
        return cls(
            config,
            services.config_manager,
            services.transcription_service,
            services.file_service,
            services.audio_service,
        )

    def _ensure_directories(self) -> None:
        """Ensure required directories exist for audio I/O.

        Creates the input and output directories if they don't exist.
        """
        # Ensure input directory exists
        input_dir = self.config_manager.get("AUDIO_INPUT_DIR")
        if not input_dir:
            input_dir = os.path.join(os.getcwd(), "input")
            os.environ["AUDIO_INPUT_DIR"] = input_dir
            self.config_manager.set("AUDIO_INPUT_DIR", input_dir)
            logger.info(f"AUDIO_INPUT_DIR not set, using default: {input_dir}")

            if not os.path.exists(input_dir):
                os.makedirs(input_dir, exist_ok=True)
                logger.info(f"Created input directory: {input_dir}")

        # Ensure output directory exists
        output_dir = self.config_manager.get("AUDIO_OUTPUT_DIR")
        if not output_dir:
            output_dir = os.path.join(os.getcwd(), "output")
            os.environ["AUDIO_OUTPUT_DIR"] = output_dir
            self.config_manager.set("AUDIO_OUTPUT_DIR", output_dir)
            logger.info(
                f"AUDIO_OUTPUT_DIR not set, using default: {output_dir}"
            )

            if not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
                logger.info(f"Created output directory: {output_dir}")

    async def _record_audio_async(self, duration: int) -> str:
        """Record audio from microphone asynchronously.

        Args:
            duration: Recording duration in seconds

        Returns:
            str: Path to the recorded audio file

        Raises:
            AudioRecordingError: If recording fails
        """
        try:
            # Run the recording operation in a thread pool since PyAudio is blocking
            logger.info(f"Recording audio for {duration} seconds...")
            print(f"Recording audio for {duration} seconds...")

            # Use asyncio.to_thread to run the blocking recording operation
            # without blocking the event loop
            audio_path = await asyncio.to_thread(
                self.audio_service.record_audio, duration=duration
            )

            logger.info(f"Audio recorded and saved to: {audio_path}")
            print(f"Audio recorded and saved to: {audio_path}")
            return audio_path
        except Exception as e:
            error_msg = f"Failed to record audio: {e}"
            logger.error(error_msg)
            raise AudioRecordingError(error_msg, error_code="RECORD_FAILED")

    async def _save_transcription_async(
        self, transcription: str, output_path: Optional[str] = None
    ) -> str:
        """Save transcription to file asynchronously.

        Args:
            transcription: The transcription text to save
            output_path: Optional specific path to save to

        Returns:
            str: Path to the saved transcription file

        Raises:
            FileOperationError: If saving fails
        """
        try:
            # Use provided path or generate timestamped one
            if not output_path and self.config.get("save_transcript", False):
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                output_dir = self.config_manager.get("AUDIO_OUTPUT_DIR", "")
                if output_dir:
                    output_path = os.path.join(
                        output_dir,
                        f"transcript_{timestamp}.txt",
                    )

            if output_path:
                # Run the file saving operation in a thread
                await asyncio.to_thread(
                    self.file_service.save_text, transcription, output_path
                )
                logger.info(f"Transcription saved to: {output_path}")
                print(f"Transcription saved to: {output_path}")
                return output_path

            return ""
        except Exception as e:
            error_msg = f"Failed to save transcription: {e}"
            logger.error(error_msg)
            raise FileOperationError(error_msg, error_code="SAVE_FAILED")

    async def handle_audio_in(self) -> str:
        """Handle audio input (transcription) pipeline asynchronously.

        This method supports two modes:
        1. Transcribe an existing audio file if audio_path is provided
        2. Record from microphone and transcribe if no audio_path is provided

        Returns:
            str: The transcription result

        Raises:
            AudioServiceError: If audio recording or transcription fails
            FileOperationError: If saving the transcription fails

        Example:
            ```python
            config = {"duration": 10, "model": "small"}
            controller = AudioPipelineController(
                config, config_manager, transcription_service, file_service, audio_service
            )
            transcription = await controller.handle_audio_in()
            print(transcription)
            ```
        """
        # Use guard clause for determining audio path
        audio_path = self.config.get("audio_path")
        if not audio_path:
            # Record from microphone if no path provided
            audio_path = await self._record_audio_async(
                self.config.get("duration", 5)
            )

        # Transcribe the audio - use a thread pool for CPU-intensive work
        try:
            # Run the transcription operation in a thread pool
            transcription = await asyncio.to_thread(
                self.transcription_service.transcribe_audio,
                audio_path,
                model_size=self.config.get("model"),
                language=self.config.get("language"),
            )
        except Exception as e:
            error_msg = f"Failed to transcribe audio: {e}"
            logger.error(error_msg)
            raise TranscriptionError(error_msg, error_code="TRANSCRIBE_FAILED")

        # Save transcript if needed
        output_path = self.config.get("output_path")
        await self._save_transcription_async(transcription, output_path)

        # Always print the transcription
        print(f"Transcription: {transcription}")

        # Always return the text
        return transcription

    async def resolve_text_source_async(self) -> str:
        """Resolve the input source text from config or environment asynchronously.

        Returns:
            str: The resolved text content

        Example:
            ```python
            controller = AudioPipelineController(
                {"data_source": "hello.txt"}, config_manager, transcription_service, file_service, audio_service
            )
            text = await controller.resolve_text_source_async()
            ```
        """
        # Guard clause: check if source exists
        source = self.config.get("data_source")
        if not source:
            logger.warning("No source text found in config.")
            return "no text found"

        # Guard clause: check if it's a file path
        if not os.path.isfile(source):
            return str(source)

        # Try to read the file
        try:
            # Run the file reading operation in a thread pool
            content = await asyncio.to_thread(
                self.file_service.read_text, source
            )
            return str(content)
        except Exception as e:
            error_msg = f"Failed to read source file: {e}"
            logger.error(error_msg)
            raise FileOperationError(error_msg, error_code="READ_FAILED")

    async def handle_audio_out(self) -> str:
        """Handle audio output (synthesis) pipeline asynchronously.

        Returns:
            str: Path to the output audio file

        Raises:
            AudioServiceError: If synthesis or playback fails
            FileOperationError: If file operations fail

        Example:
            ```python
            config = {"data_source": "Hello, world!", "play_audio": True}
            controller = AudioPipelineController(
                config, config_manager, transcription_service, file_service, audio_service
            )
            audio_path = await controller.handle_audio_out()
            ```
        """
        try:
            # Get the text to synthesize
            text = await self.resolve_text_source_async()
        except FileOperationError as e:
            # Re-raise with additional context
            raise FileOperationError(
                f"Failed to resolve text source: {e}",
                error_code="SOURCE_FAILED",
                details={"original_error": str(e)},
            )

        # Guard clause: validate text
        if not text or text == "no text found":
            error_msg = "No valid text to synthesize."
            logger.warning(error_msg)
            raise AudioServiceError(error_msg, error_code="EMPTY_TEXT")

        # Synthesize audio - run in thread pool since TTS is CPU-intensive
        try:
            audio_data = await asyncio.to_thread(
                TextToSpeechService.synthesize, text
            )
        except Exception as e:
            error_msg = f"Error synthesizing audio: {e}"
            logger.error(error_msg)
            raise AudioServiceError(error_msg, error_code="SYNTHESIS_FAILED")

        # Determine output path
        output_path = self.config.get(
            "output_path"
        ) or await asyncio.to_thread(
            self.file_service.generate_temp_output_path
        )

        # Save audio to file - file I/O operations in thread pool
        try:
            await asyncio.to_thread(
                self.file_service.save, audio_data, output_path
            )
            logger.info(f"Audio saved to: {output_path}")
        except Exception as e:
            error_msg = f"Error saving audio file: {e}"
            logger.error(error_msg)
            raise FileOperationError(error_msg, error_code="SAVE_FAILED")

        # Play audio if enabled - in thread pool since playback is blocking
        if self.config.get("play_audio", True):
            try:
                await asyncio.to_thread(AudioPlaybackService.play, audio_data)
                logger.info("Audio playback completed")
            except Exception as e:
                error_msg = f"Error playing audio: {e}"
                logger.error(error_msg)
                raise AudioServiceError(
                    error_msg, error_code="PLAYBACK_FAILED"
                )

        # Return text instead of path if flagged (for testing or debugging)
        if self.config.get("return_text_output", False):
            return text

        return output_path

    async def _get_latest_transcription_async(self) -> Optional[str]:
        """Get the latest transcription from files asynchronously.

        Returns:
            Optional[str]: The latest transcription or None if not found

        Example:
            ```python
            controller = AudioPipelineController(
                {}, config_manager, transcription_service, file_service, audio_service
            )
            latest_text = await controller._get_latest_transcription_async()
            if latest_text:
                print(f"Latest transcription: {latest_text}")
            ```
        """
        try:
            return await asyncio.to_thread(
                self.file_service.load_latest_transcription
            )
        except FileOperationError as e:
            logger.warning(f"Failed to load latest transcription: {e}")
            return None
        except Exception as e:
            error_msg = f"Unexpected error loading transcription: {e}"
            logger.error(error_msg)
            return None

    async def handle_conversation_loop(
        self, max_turns: int = 5
    ) -> List[Dict[str, str]]:
        """Run a bidirectional conversation loop between user and machine.

        This demonstrates the benefit of async patterns for conversational interfaces.

        Args:
            max_turns: Maximum number of conversation turns

        Returns:
            List[Dict[str, str]]: Conversation history with user and machine messages

        Example:
            ```python
            controller = AudioPipelineController(
                {}, config_manager, transcription_service, file_service, audio_service
            )
            conversation = await controller.handle_conversation_loop()
            ```
        """
        conversation_history = []

        print(f"Starting conversation loop (max {max_turns} turns)...")

        for turn in range(max_turns):
            print(f"\n--- Turn {turn+1}/{max_turns} ---")

            # 1. Record and transcribe user input (audio in)
            try:
                # Record user speech
                print("Your turn to speak...")
                user_text = await self.handle_audio_in()
                conversation_history.append(
                    {"role": "user", "content": user_text}
                )

                # Check for conversation end
                if (
                    "goodbye" in user_text.lower()
                    or "exit" in user_text.lower()
                ):
                    print("Ending conversation as requested.")
                    break

            except Exception as e:
                logger.error(f"Error in user input handling: {e}")
                print(f"Sorry, I couldn't understand that. Error: {e}")
                continue

            # 2. Generate response (could connect to an LLM in a real implementation)
            try:
                # Simulate LLM response generation (non-blocking)
                print("Generating response...")
                await asyncio.sleep(0.5)  # Simulate thinking time

                # Generate simple response based on user input
                if "hello" in user_text.lower() or "hi" in user_text.lower():
                    response = "Hello! How can I help you today?"
                elif "how are you" in user_text.lower():
                    response = "I'm functioning well, thank you for asking. How about you?"
                elif "weather" in user_text.lower():
                    response = "I'm sorry, I don't have access to weather information at the moment."
                else:
                    response = (
                        f"I heard you say: {user_text}. That's interesting!"
                    )

                conversation_history.append(
                    {"role": "assistant", "content": response}
                )

                # Configure TTS output
                self.config["data_source"] = response

                # 3. Synthesize and play response (audio out)
                print("Assistant response:")
                print(f"'{response}'")
                await self.handle_audio_out()

            except Exception as e:
                logger.error(f"Error in response generation or playback: {e}")
                print(f"Sorry, I couldn't respond properly. Error: {e}")

        print("\nConversation loop completed.")
        return conversation_history
