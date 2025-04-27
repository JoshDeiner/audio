"""Refactored audio pipeline controller with plugin support.

This module provides the controller that orchestrates the audio processing
pipelines with support for plugins and extensibility.
"""

import logging
import os
import time
from typing import Any, Dict, Optional

from config.configuration_manager import ConfigurationManager
from plugins.plugin_manager import PluginManager
from services.audio_playback_service import AudioPlaybackService
from services.audio_service import AudioRecordingService
from services.exceptions import (
    AudioRecordingError,
    AudioServiceError,
    FileOperationError,
    TranscriptionError,
)
from services.file_service import FileService
from services.services_factory import ServiceFactory
from services.text_to_speech_service import TextToSpeechService
from services.transcription_service import TranscriptionService

logger = logging.getLogger(__name__)


class AudioPipelineController:
    """Controller for audio processing pipelines with plugin support.

    This controller coordinates the various services required for audio
    processing, including recording, transcription, and synthesis.
    It supports extensibility through plugins.

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
                "duration": 10,
                "transcription_plugin": "whisper_transcription"
            }
            controller = AudioPipelineController(config)
            ```
        """
        self.config = config
        self.config_manager = ConfigurationManager
        
        # Initialize service factory
        self.service_factory = ServiceFactory(self.config_manager)
        self.service_factory.initialize()
        
        # Set up plugin manager
        self.plugin_manager = PluginManager(self.config_manager)
        
        # Create services using factory
        self.transcription_service = self.service_factory.create_transcription_service(config)
        self.file_service = self.service_factory.create_file_service()

        # Ensure directories exist
        self._ensure_directories()
        
        # Initialize processing hooks
        self._pre_processing_hooks = []
        self._post_processing_hooks = []
        
        # Register any processing hooks specified in configuration
        self._register_hooks()

    def _ensure_directories(self) -> None:
        """Ensure required directories exist for audio I/O."""
        input_dir = self.config_manager.get("AUDIO_INPUT_DIR")
        if not input_dir:
            input_dir = os.path.join(os.getcwd(), "input")
            self.config_manager.set("AUDIO_INPUT_DIR", input_dir)
            logger.info(f"AUDIO_INPUT_DIR not set, using default: {input_dir}")

        if not os.path.exists(input_dir):
            os.makedirs(input_dir, exist_ok=True)
            logger.info(f"Created input directory: {input_dir}")

        output_dir = self.config_manager.get("AUDIO_OUTPUT_DIR")
        if not output_dir:
            output_dir = os.path.join(os.getcwd(), "output")
            self.config_manager.set("AUDIO_OUTPUT_DIR", output_dir)
            logger.info(f"AUDIO_OUTPUT_DIR not set, using default: {output_dir}")

        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            logger.info(f"Created output directory: {output_dir}")

    def _register_hooks(self) -> None:
        """Register processing hooks from configuration."""
        # Get pre-processing plugins
        pre_plugins = self.config.get("pre_processing_plugins", [])
        for plugin_id in pre_plugins:
            plugin = self.plugin_manager.get_preprocessing_plugin(plugin_id)
            if plugin:
                self._pre_processing_hooks.append(plugin)
                logger.info(f"Registered pre-processing plugin: {plugin_id}")
            else:
                logger.warning(f"Pre-processing plugin not found: {plugin_id}")
                
        # Get post-processing (output) plugins
        post_plugins = self.config.get("output_plugins", [])
        for plugin_id in post_plugins:
            plugin = self.plugin_manager.get_output_plugin(plugin_id)
            if plugin:
                self._post_processing_hooks.append(plugin)
                logger.info(f"Registered output plugin: {plugin_id}")
            else:
                logger.warning(f"Output plugin not found: {plugin_id}")

    def register_pre_processing_hook(self, hook: Any) -> None:
        """Register a pre-processing hook.

        Args:
            hook: The hook to register (must have a process_audio method)
        """
        self._pre_processing_hooks.append(hook)
        logger.info(f"Registered pre-processing hook: {hook}")

    def register_post_processing_hook(self, hook: Any) -> None:
        """Register a post-processing hook.

        Args:
            hook: The hook to register (must have a handle_transcription method)
        """
        self._post_processing_hooks.append(hook)
        logger.info(f"Registered post-processing hook: {hook}")

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
            recording_service = self.service_factory.create_audio_recording_service()
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
                output_dir = self.config_manager.get("AUDIO_OUTPUT_DIR", "")
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
        """
        # Use guard clause for determining audio path
        audio_path = self.config.get("audio_path")
        if not audio_path:
            # Record from microphone if no path provided
            audio_path = self._record_audio(self.config.get("duration", 5))

        # Run pre-processing hooks if any
        if self._pre_processing_hooks:
            try:
                # Read audio file
                audio_format_plugin = self.plugin_manager.get_audio_format_plugin()
                if audio_format_plugin:
                    audio_data, sample_rate = audio_format_plugin.read_file(audio_path)
                    
                    # Apply pre-processing hooks
                    for hook in self._pre_processing_hooks:
                        audio_data, sample_rate = hook.process_audio(
                            audio_data, sample_rate
                        )
                    
                    # Save processed audio to a temporary file
                    temp_path = os.path.join(
                        os.path.dirname(audio_path),
                        f"processed_{os.path.basename(audio_path)}",
                    )
                    audio_format_plugin.write_file(temp_path, audio_data, sample_rate)
                    audio_path = temp_path
                    logger.info(f"Pre-processed audio saved to: {audio_path}")
            except Exception as e:
                logger.warning(f"Error in pre-processing: {e}")
                # Continue with original audio if pre-processing fails

        # Transcribe the audio
        try:
            # Get plugin ID from config if specified
            plugin_id = self.config.get("transcription_plugin")
            if plugin_id:
                # Use plugin-specific options if available
                options = self.config.get("transcription_options", {})
                
                # Get the plugin
                plugin = self.plugin_manager.get_transcription_plugin(plugin_id)
                
                if plugin:
                    # Use the plugin directly
                    transcription = plugin.transcribe(
                        audio_path,
                        language=self.config.get("language"),
                        options=options,
                    )
                else:
                    # Fall back to service
                    transcription = self.transcription_service.transcribe_audio(
                        audio_path,
                        model_size=self.config.get("model"),
                        language=self.config.get("language"),
                    )
            else:
                # Use the service
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

        # Run post-processing hooks
        if self._post_processing_hooks:
            metadata = {
                "source_file": audio_path,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "model": self.config.get("model", "unknown"),
                "language": self.config.get("language", "auto"),
            }
            
            for hook in self._post_processing_hooks:
                try:
                    hook.handle_transcription(transcription, metadata)
                except Exception as e:
                    logger.warning(f"Error in post-processing hook: {e}")

        # Always print the transcription
        print(f"Transcription: {transcription}")

        # Always return the text
        return transcription

    def resolve_text_source(self) -> str:
        """Resolve the input source text from config or environment.

        Returns:
            str: The resolved text content
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
            return str(self.file_service.read_text(source))
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
            # Get TTS service
            tts_service = self.service_factory.create_tts_service()
            
            # Use plugin if specified in config
            tts_plugin = self.config.get("tts_plugin")
            if tts_plugin:
                # Plugin support for TTS could be added in the future
                pass
                
            audio_data = tts_service.synthesize(text)
        except Exception as e:
            error_msg = f"Error synthesizing audio: {e}"
            logger.error(error_msg)
            raise AudioServiceError(error_msg, error_code="SYNTHESIS_FAILED")

        # Determine output path
        output_path = (
            self.config.get("output_path")
            or self.file_service.generate_temp_output_path()
        )

        # Save audio to file
        try:
            # Use audio format plugin if available
            audio_format_plugin = self.plugin_manager.get_audio_format_plugin()
            if audio_format_plugin and isinstance(audio_data, tuple):
                audio_format_plugin.write_file(
                    output_path, audio_data[0], audio_data[1]
                )
            else:
                # Fall back to file service
                self.file_service.save(audio_data, output_path)
                
            logger.info(f"Audio saved to: {output_path}")
        except Exception as e:
            error_msg = f"Error saving audio file: {e}"
            logger.error(error_msg)
            raise FileOperationError(error_msg, error_code="SAVE_FAILED")

        # Play audio if enabled
        if self.config.get("play_audio", True):
            try:
                playback_service = self.service_factory.create_audio_playback_service()
                playback_service.play(audio_data)
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

    def cleanup(self) -> None:
        """Clean up resources used by the controller."""
        # Clean up services
        if hasattr(self.transcription_service, 'cleanup'):
            self.transcription_service.cleanup()
            
        if hasattr(self.file_service, 'cleanup'):
            self.file_service.cleanup()
            
        # Clean up plugin manager
        self.plugin_manager.cleanup()
        
        logger.info("Audio pipeline controller cleaned up")