"""Transcription service for audio transcription tool."""

import logging
import os
import time
from typing import Dict, Optional

from colorama import Fore, Style
from faster_whisper import WhisperModel

from services.exceptions import FileOperationError, TranscriptionError
from services.file_service import FileService

logger = logging.getLogger(__name__)


class TranscriptionService:
    """Service for transcribing audio using faster-whisper."""

    def __init__(self) -> None:
        """Initialize the transcription service."""
        self.file_service = FileService()

    def transcribe_audio(
        self,
        audio_file_path: str,
        model_size: Optional[str] = None,
        language: Optional[str] = None,
    ) -> str:
        """Transcribe audio file using faster-whisper model.

        Args:
            audio_file_path: Path to the audio file to transcribe
            model_size: Whisper model size (tiny, base, small, medium, large)
            language: Language code to use (e.g., 'en' for English).
                If provided, skips language detection.

        Returns:
            str: Transcribed text

        Raises:
            TranscriptionError: If transcription fails
            FileOperationError: If file operations fail
        """
        # Validate input file
        if not self._is_valid_audio_file(audio_file_path):
            raise TranscriptionError("Invalid or corrupted audio file")

        # Get model configuration
        model_config = self._get_whisper_model_config(model_size)

        # Load and run the model
        try:
            transcription = self._run_whisper_transcription(
                audio_file_path, model_config, language
            )

            # Save transcription to output file
            self._save_transcription_to_file(audio_file_path, transcription)

            return transcription

        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            raise TranscriptionError(f"Failed to transcribe audio: {str(e)}")

    def _is_valid_audio_file(self, audio_file_path: str) -> bool:
        """Check if the audio file is valid.

        Args:
            audio_file_path: Path to the audio file

        Returns:
            bool: True if the file is valid, False otherwise
        """
        if not os.path.exists(audio_file_path):
            logger.error(f"Audio file not found: {audio_file_path}")
            return False

        return self.file_service.validate_audio_file(audio_file_path)

    def _get_whisper_model_config(
        self, model_size: Optional[str] = None
    ) -> Dict[str, str]:
        """Get Whisper model configuration.

        Args:
            model_size: Whisper model size

        Returns:
            Dict[str, str]: Model configuration dictionary
        """
        # Get model size from environment or use default/provided value
        if not model_size:
            model_size = os.environ.get("WHISPER_MODEL", "tiny")

        # Validate model size
        valid_sizes = ["tiny", "base", "small", "medium", "large"]
        if model_size not in valid_sizes:
            logger.warning(
                f"Invalid model size: {model_size}. Using 'tiny' instead."
            )
            model_size = "tiny"

        # Get compute type from environment or use default
        compute_type = os.environ.get("WHISPER_COMPUTE_TYPE", "int8")

        # Get device from environment or use default
        device = os.environ.get("WHISPER_DEVICE", "cpu")

        return {
            "model_size": model_size,
            "compute_type": compute_type,
            "device": device,
        }

    def _run_whisper_transcription(
        self,
        audio_file_path: str,
        model_config: Dict[str, str],
        language: Optional[str] = None,
    ) -> str:
        """Run the Whisper model transcription.

        Args:
            audio_file_path: Path to the audio file
            model_config: Model configuration dictionary
            language: Language code to use (e.g., 'en' for English).
                If provided, skips language detection.

        Returns:
            str: Transcribed text

        Raises:
            TranscriptionError: If transcription fails
        """
        logger.info(f"Loading Whisper model: {model_config['model_size']}")
        logger.info(f"Using compute type: {model_config['compute_type']}")
        logger.info(f"Using device: {model_config['device']}")

        try:
            # Initialize the model
            model = WhisperModel(
                model_config["model_size"],
                device=model_config["device"],
                compute_type=model_config["compute_type"],
            )
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise TranscriptionError(
                f"""Failed to load Whisper model.
                Check if the model cache directory is properly mounted: {e}"""
            )

        # Run transcription
        logger.info(f"Transcribing audio file: {audio_file_path}")
        print(f"{Fore.CYAN}Transcribing audio...{Style.RESET_ALL}")

        # Set up transcription parameters
        transcription_options = {"beam_size": 5}

        # If language is specified, use it to skip language detection
        if language:
            logger.info(f"Using specified language: {language}")
            transcription_options["language"] = language  # type: ignore
            print(
                f"{Fore.CYAN}Using language: {Fore.YELLOW}{language}{Style.RESET_ALL}"
            )

        # Run transcription with the specified options
        segments, info = model.transcribe(
            audio_file_path, **transcription_options
        )

        # Collect transcription segments
        transcription = " ".join([segment.text for segment in segments])

        if language:
            logger.info(
                f"Transcription complete (using specified language: {language})"
            )
        else:
            logger.info(
                f"Transcription complete (detected language: {info.language}, "
                f"probability: {info.language_probability:.2f})"
            )

        return transcription.strip()

    def _save_transcription_to_file(
        self, audio_file_path: str, transcription: str
    ) -> str:
        """Save transcription to a text file.

        Args:
            audio_file_path: Path to the original audio file
            transcription: Transcribed text

        Returns:
            str: Path to the saved transcription file

        Raises:
            FileOperationError: If saving fails
        """
        # Get output directory from environment or use default
        output_dir = self.file_service.sanitize_path(
            os.environ.get("AUDIO_OUTPUT_DIR", "output")
        )

        try:
            # Create output directory if it doesn't exist
            self.file_service.prepare_directory(output_dir)

            # Generate output filename based on input filename
            base_name = os.path.basename(audio_file_path)
            file_name = os.path.splitext(base_name)[0]
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            output_file = os.path.join(
                output_dir, f"{file_name}_{timestamp}.txt"
            )

            # Save transcription to file
            with open(output_file, "w") as f:
                f.write(transcription)

            logger.info(f"Transcription saved to: {output_file}")
            return output_file

        except (IOError, OSError) as e:
            logger.error(f"Failed to save transcription: {e}")
            raise FileOperationError(f"Failed to save transcription: {e}")
        except Exception as e:
            logger.error(f"Unexpected error saving transcription: {e}")
            raise FileOperationError(f"Failed to save transcription: {e}")
