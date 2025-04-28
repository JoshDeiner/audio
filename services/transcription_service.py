"""Transcription service for audio transcription tool."""

import logging
import os
import time
from typing import Dict, Optional

from colorama import Fore, Style
from faster_whisper import WhisperModel

from config.configuration_manager import ConfigurationManager
from services.exceptions import (
    FileOperationError,
    SecurityError,
    TranscriptionError,
)
from services.file_service import FileService

logger = logging.getLogger(__name__)


class TranscriptionService:
    """Service for transcribing audio using faster-whisper."""

    def __init__(
        self, config_manager: Optional[ConfigurationManager] = None
    ) -> None:
        """Initialize the transcription service.

        Args:
            config_manager: Optional configuration manager instance
        """
        self.file_service = FileService()
        self.config_manager = config_manager or ConfigurationManager

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
            ValueError: If input parameters are invalid
            SecurityError: If file path is invalid or potentially malicious
            TranscriptionError: If transcription fails
            FileOperationError: If file operations fail
        """
        # Validate input parameters
        if not audio_file_path:
            logger.error("Audio file path cannot be empty")
            raise ValueError("Audio file path cannot be empty")

        # Validate model_size if provided
        valid_model_sizes = ["tiny", "base", "small", "medium", "large"]
        if model_size and model_size not in valid_model_sizes:
            logger.error(
                f"Invalid model size: {model_size}. Must be one of {valid_model_sizes}"
            )
            raise ValueError(
                f"Invalid model size: {model_size}. Must be one of {valid_model_sizes}"
            )

        # Validate language code if provided
        if language:
            # Simple validation - RFC 5646 language tags are typically 2-7 chars
            if not isinstance(language, str) or not (2 <= len(language) <= 7):
                logger.error(f"Invalid language code: {language}")
                raise ValueError(f"Invalid language code: {language}")

            # Only allow alphanumeric chars and hyphen in language code
            if not all(c.isalnum() or c == "-" for c in language):
                logger.error(
                    f"Invalid characters in language code: {language}"
                )
                raise ValueError(
                    f"Invalid characters in language code: {language}"
                )

        # Validate input file - this may raise SecurityError
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

        except SecurityError as e:
            # Pass through security errors
            logger.error(f"Security error during transcription: {e}")
            raise e
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            raise TranscriptionError(f"Failed to transcribe audio: {str(e)}")

    def _is_valid_audio_file(self, audio_file_path: str) -> bool:
        """Check if the audio file is valid.

        Args:
            audio_file_path: Path to the audio file

        Returns:
            bool: True if the file is valid, False otherwise

        Raises:
            SecurityError: If file path is invalid or potentially malicious
        """
        # Input validation for audio_file_path
        if not audio_file_path or not isinstance(audio_file_path, str):
            logger.error("Audio file path must be a non-empty string")
            return False

        # Additional format validation to ensure file has audio extension
        valid_extensions = [".wav", ".mp3", ".flac", ".ogg", ".m4a"]
        if not any(
            audio_file_path.lower().endswith(ext) for ext in valid_extensions
        ):
            logger.warning(
                f"File does not have a standard audio extension: {audio_file_path}"
            )
            # Continue but log warning

        # Let FileService handle path validation and audio file validation
        try:
            return self.file_service.validate_audio_file(audio_file_path)
        except SecurityError as e:
            logger.error(f"Security error validating audio file: {e}")
            raise SecurityError(
                f"Security validation failed for audio file: {e}"
            )
        except Exception as e:
            logger.error(f"Error validating audio file: {e}")
            return False

    def _get_whisper_model_config(
        self, model_size: Optional[str] = None
    ) -> Dict[str, str]:
        """Get Whisper model configuration.

        Args:
            model_size: Whisper model size

        Returns:
            Dict[str, str]: Model configuration dictionary

        Raises:
            ValueError: If model configuration is invalid
        """
        # Get model size from config or use provided value
        if not model_size:
            model_size = self.config_manager.get("WHISPER_MODEL", "tiny")

        # Ensure model_size is a string
        if not isinstance(model_size, str):
            logger.error(f"Invalid model size type: {type(model_size)}")
            raise ValueError(
                f"Model size must be a string, got {type(model_size)}"
            )

        # Validate model size
        valid_sizes = ["tiny", "base", "small", "medium", "large"]
        if model_size not in valid_sizes:
            logger.warning(
                f"Invalid model size: {model_size}. Using 'tiny' instead."
            )
            model_size = "tiny"

        # Get compute type and device from config
        compute_type = self.config_manager.get("WHISPER_COMPUTE_TYPE", "int8")
        device = self.config_manager.get("WHISPER_DEVICE", "cpu")

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
            SecurityError: If file path is invalid or potentially malicious
            FileOperationError: If saving fails
        """
        # Input validation
        if not transcription:
            logger.warning("Empty transcription content")
            transcription = "(No transcription available)"

        if not audio_file_path or not isinstance(audio_file_path, str):
            logger.error("Invalid audio file path")
            raise ValueError("Invalid audio file path")

        # Sanitize original file path for security
        try:
            sanitized_audio_path = self.file_service.sanitize_path(
                audio_file_path
            )
        except SecurityError:
            # If the original path fails validation, use a generic name instead
            sanitized_audio_path = "audio_file"

        # Get output directory from config
        output_dir = self.file_service.sanitize_path(
            self.config_manager.get("AUDIO_OUTPUT_DIR", "output")
        )

        try:
            # Create output directory if it doesn't exist
            self.file_service.prepare_directory(output_dir)

            # Generate output filename based on input filename but sanitize the filename
            # Remove any potentially dangerous characters from the filename
            base_name = os.path.basename(sanitized_audio_path)
            file_name = os.path.splitext(base_name)[0]
            # Keep only alphanumeric chars and some safe punctuation
            safe_file_name = "".join(
                c for c in file_name if c.isalnum() or c in "-_"
            )
            if not safe_file_name:
                safe_file_name = "transcription"  # Fallback if no valid chars

            timestamp = time.strftime("%Y%m%d-%H%M%S")
            output_file = os.path.join(
                output_dir, f"{safe_file_name}_{timestamp}.txt"
            )

            # Use the file service to save the text
            return self.file_service.save_text(transcription, output_file)

        except SecurityError as e:
            # Pass through security errors
            logger.error(f"Security error saving transcription: {e}")
            raise e
        except (IOError, OSError) as e:
            logger.error(f"Failed to save transcription: {e}")
            raise FileOperationError(f"Failed to save transcription: {e}")
        except Exception as e:
            logger.error(f"Unexpected error saving transcription: {e}")
            raise FileOperationError(f"Failed to save transcription: {e}")
