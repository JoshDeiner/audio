"""Audio pipeline controller for the audio package."""

import logging
import os
from typing import Dict, Optional

from services.audio_playback_service import AudioPlaybackService
from services.file_service import FileService
from services.text_to_speech_service import TextToSpeechService
from services.transcription_service import TranscriptionService

logger = logging.getLogger(__name__)


class AudioPipelineController:
    """Controller for audio processing pipelines."""

    def __init__(self, config: Dict[str, any]) -> None:
        """Initialize the controller with configuration.

        Args:
            config: Configuration dictionary with pipeline options
        """
        self.config = config
        self.transcription_service = TranscriptionService()
        self.file_service = FileService()

    def handle_audio_in(self) -> str:
        """Handle audio input (transcription) pipeline.

        Returns:
            str: The transcription result
        """
        audio_path = self.config.get("audio_path")
        if not audio_path:
            raise ValueError(
                "Audio path must be provided for audio-in pipeline"
            )

        transcription = self.transcription_service.transcribe_audio(
            audio_path,
            model_size=self.config.get("model"),
            language=self.config.get("language"),
        )

        print(f"Transcription: {transcription}")

        if self.config.get("save_transcript", False):
            self.file_service.save_text(transcription, f"{audio_path}.txt")

        return transcription

    def resolve_text_source(self) -> str:
        """To resolve the input source text from config or environment.

        Returns:
            str: The resolved text content
        """
        # Prefer config text if set
        source = self.config.get("datasource")
        if not source:
            logging.warning("No source text found in config.")
            return "no text found"

        # If it's not a file path, return as is
        if not os.path.isfile(source):
            return source

        # Try to read the file
        try:
            return FileService.read_text(source)
        except Exception as e:
            logging.error(f"Failed to read source file: {e}")
            return "error reading file"

    def handle_audio_out(self) -> str:
        """Handle audio output (synthesis) pipeline.

        Returns:
            str: Path to the output audio file
        """

        text = self.resolve_text_source()

        if not text or text == "no text found":
            logger.warning("No valid text to synthesize.")
            return

        # Synthesize audio
        try:
            audio_data = TextToSpeechService.synthesize(text)
        except Exception as e:
            logger.error(f"Error synthesizing audio: {e}")
            return

        # Save audio to file
        output_path = (
            self.config.get("output_path")
            or FileService.generate_temp_output_path()
        )

        try:
            self.file_service.save(audio_data, output_path)
        except Exception as e:
            logger.error(f"Error saving audio file: {e}")
            return f"Error saving audio file: {e}"

        # Play audio if enabled
        if self.config.get("play_audio", True):
            try:
                AudioPlaybackService.play(audio_data)
            except Exception as e:
                logger.error(f"Error playing audio: {e}")
                return f"Error playing audio: {e}"

        # Return text instead of path if flagged (for testing or debugging)
        if self.config.get("return_text_output", False):
            return text

        return output_path

    def _get_latest_transcription(self) -> Optional[str]:
        """Get the latest transcription from files.

        Returns:
            Optional[str]: The latest transcription or None if not found
        """
        try:
            return FileService.load_latest_transcription()
        except Exception as e:
            logger.warning(f"Failed to load latest transcription: {e}")
            return None
