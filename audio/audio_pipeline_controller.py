"""Audio pipeline controller for the audio package.

This module provides the controller that orchestrates the audio processing
pipelines for both input (recording/transcription) and output (synthesis/playback).

Author: Claude Code
Created: 2025-04-27
"""

import logging
import os
import time
from typing import Any
from typing import Dict
from typing import Optional

from services.audio_playback_service import AudioPlaybackService
from services.audio_service import AudioRecordingService
from services.exceptions import (
    AudioRecordingError,
    AudioServiceError,
    FileOperationError,
    TranscriptionError,
)
from services.file_service import FileService
from services.text_to_speech_service import TextToSpeechService
from services.transcription_service import TranscriptionService

logger = logging.getLogger(__name__)


class AudioPipelineController:
    """Controller for audio processing pipelines.

    This controller coordinates the various services required for audio
    processing, including recording, transcription, and synthesis.

    Attributes:
        config: Configuration dictionary with pipeline options
        transcription_service: Service for audio transcription
        file_service: Service for file operations
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize the controller with configuration.

        Args:
            config: Configuration dictionary with pipeline options

        Example:
            ```python
            config = {
                "model": "small",
                "language": "en",
                "duration": 10
            }
            controller = AudioPipelineController(config)
            ```
        """
        self.config = config
        self.transcription_service = TranscriptionService()
        self.file_service = FileService()

        # Ensure directories exist
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Ensure required directories exist for audio I/O.

        Creates the input and output directories if they don't exist.
        """
        # Ensure input directory exists
        if not os.environ.get("AUDIO_INPUT_DIR"):
            input_dir = os.path.join(os.getcwd(), "input")
            os.environ["AUDIO_INPUT_DIR"] = input_dir
            logger.info(f"AUDIO_INPUT_DIR not set, using default: {input_dir}")

            if not os.path.exists(input_dir):
                os.makedirs(input_dir, exist_ok=True)
                logger.info(f"Created input directory: {input_dir}")

        # Ensure output directory exists
        if not os.environ.get("AUDIO_OUTPUT_DIR"):
            output_dir = os.path.join(os.getcwd(), "output")
            os.environ["AUDIO_OUTPUT_DIR"] = output_dir
            logger.info(
                f"AUDIO_OUTPUT_DIR not set, using default: {output_dir}"
            )

            if not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
                logger.info(f"Created output directory: {output_dir}")

    def _record_audio(self, duration: int) -> str:
        """Record audio from microphone.

        Args:
            duration: Recording duration in seconds

        Returns:
            str: Path to the recorded audio file

        Raises:
            AudioRecordingError: If recording fails
        """
        try:
            recording_service = AudioRecordingService()
            logger.info(f"Recording audio for {duration} seconds...")
            print(f"Recording audio for {duration} seconds...")

            audio_path = recording_service.record_audio(duration=duration)
            logger.info(f"Audio recorded and saved to: {audio_path}")
            print(f"Audio recorded and saved to: {audio_path}")
            return audio_path
        except Exception as e:
            error_msg = f"Failed to record audio: {e}"
            logger.error(error_msg)
            raise AudioRecordingError(error_msg, error_code="RECORD_FAILED")

    def _save_transcription(
        self, transcription: str, output_path: Optional[str] = None
    ) -> str:
        """Save transcription to file.

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
                output_dir = os.environ.get("AUDIO_OUTPUT_DIR", "")
                if output_dir:
                    output_path = os.path.join(
                        output_dir,
                        f"transcript_{timestamp}.txt",
                    )

            if output_path:
                self.file_service.save_text(transcription, output_path)
                logger.info(f"Transcription saved to: {output_path}")
                print(f"Transcription saved to: {output_path}")
                return output_path

            return ""
        except Exception as e:
            error_msg = f"Failed to save transcription: {e}"
            logger.error(error_msg)
            raise FileOperationError(error_msg, error_code="SAVE_FAILED")

    def handle_audio_in(self) -> str:
        """Handle audio input (transcription) pipeline.

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
            controller = AudioPipelineController(config)
            transcription = controller.handle_audio_in()
            print(transcription)
            ```
        """
        # Use guard clause for determining audio path
        audio_path = self.config.get("audio_path")
        if not audio_path:
            # Record from microphone if no path provided
            audio_path = self._record_audio(self.config.get("duration", 5))

        # Transcribe the audio
        try:
            transcription = self.transcription_service.transcribe_audio(
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
        self._save_transcription(transcription, output_path)

        # Always print the transcription
        print(f"Transcription: {transcription}")

        # Always return the text
        return transcription

    def resolve_text_source(self) -> str:
        """Resolve the input source text from config or environment.

        Returns:
            str: The resolved text content

        Example:
            ```python
            controller = AudioPipelineController({"data_source": "hello.txt"})
            text = controller.resolve_text_source()
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
            return str(FileService.read_text(source))
        except Exception as e:
            error_msg = f"Failed to read source file: {e}"
            logger.error(error_msg)
            raise FileOperationError(error_msg, error_code="READ_FAILED")

    def handle_audio_out(self) -> str:
        """Handle audio output (synthesis) pipeline.

        Returns:
            str: Path to the output audio file

        Raises:
            AudioServiceError: If synthesis or playback fails
            FileOperationError: If file operations fail

        Example:
            ```python
            config = {"data_source": "Hello, world!", "play_audio": True}
            controller = AudioPipelineController(config)
            audio_path = controller.handle_audio_out()
            ```
        """
        try:
            # Get the text to synthesize
            text = self.resolve_text_source()
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

        # Synthesize audio
        try:
            audio_data = TextToSpeechService.synthesize(text)
        except Exception as e:
            error_msg = f"Error synthesizing audio: {e}"
            logger.error(error_msg)
            raise AudioServiceError(error_msg, error_code="SYNTHESIS_FAILED")

        # Determine output path
        output_path = (
            self.config.get("output_path")
            or FileService.generate_temp_output_path()
        )

        # Save audio to file
        try:
            self.file_service.save(audio_data, output_path)
            logger.info(f"Audio saved to: {output_path}")
        except Exception as e:
            error_msg = f"Error saving audio file: {e}"
            logger.error(error_msg)
            raise FileOperationError(error_msg, error_code="SAVE_FAILED")

        # Play audio if enabled
        if self.config.get("play_audio", True):
            try:
                AudioPlaybackService.play(audio_data)
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

    def _get_latest_transcription(self) -> Optional[str]:
        """Get the latest transcription from files.

        Returns:
            Optional[str]: The latest transcription or None if not found

        Example:
            ```python
            controller = AudioPipelineController({})
            latest_text = controller._get_latest_transcription()
            if latest_text:
                print(f"Latest transcription: {latest_text}")
            ```
        """
        try:
            return FileService.load_latest_transcription()
        except FileOperationError as e:
            logger.warning(f"Failed to load latest transcription: {e}")
            return None
        except Exception as e:
            error_msg = f"Unexpected error loading transcription: {e}"
            logger.error(error_msg)
            return None
