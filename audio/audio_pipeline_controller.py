"""Audio pipeline controller for the audio package."""

import logging
import os
from typing import Any, Dict, Optional

from services.audio_playback_service import AudioPlaybackService
from services.file_service import FileService
from services.text_to_speech_service import TextToSpeechService
from services.transcription_service import TranscriptionService

logger = logging.getLogger(__name__)


class AudioPipelineController:
    """Controller for audio processing pipelines."""

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize the controller with configuration.

        Args:
            config: Configuration dictionary with pipeline options
        """
        self.config = config
        self.transcription_service = TranscriptionService()
        self.file_service = FileService()

    def handle_audio_in(self) -> str:
        """Handle audio input (transcription) pipeline.
        
        This method supports two modes:
        1. Transcribe an existing audio file if audio_path is provided
        2. Record from microphone and transcribe if no audio_path is provided

        Returns:
            str: The transcription result
        """
        audio_path = self.config.get("audio_path")
        
        # If no audio path, record from microphone
        if not audio_path:
            import os
            from services.audio_service import AudioRecordingService
            
            # Check for required environment variables
            if not os.environ.get("AUDIO_INPUT_DIR"):
                # Set default if not set
                os.environ["AUDIO_INPUT_DIR"] = os.path.join(os.getcwd(), "input")
                print(f"AUDIO_INPUT_DIR not set, using default: {os.environ['AUDIO_INPUT_DIR']}")
                
                # Make sure the directory exists
                if not os.path.exists(os.environ["AUDIO_INPUT_DIR"]):
                    os.makedirs(os.environ["AUDIO_INPUT_DIR"], exist_ok=True)
            
            recording_service = AudioRecordingService()
            
            # Get duration from config or use default
            duration = self.config.get("duration", 5)
            print(f"Recording audio for {duration} seconds...")
            
            # Record audio from microphone
            audio_path = recording_service.record_audio(duration=duration)
            print(f"Audio recorded and saved to: {audio_path}")

        # Transcribe the audio
        transcription = self.transcription_service.transcribe_audio(
            audio_path,
            model_size=self.config.get("model"),
            language=self.config.get("language"),
        )

        # Save transcript to specified output path if provided
        output_path = self.config.get("output_path")
        if output_path:
            self.file_service.save_text(transcription, output_path)
            print(f"Transcription saved to: {output_path}")
        elif self.config.get("save_transcript", False):
            # Set default output directory if not set
            import os
            if not os.environ.get("AUDIO_OUTPUT_DIR"):
                os.environ["AUDIO_OUTPUT_DIR"] = os.path.join(os.getcwd(), "output")
                if not os.path.exists(os.environ["AUDIO_OUTPUT_DIR"]):
                    os.makedirs(os.environ["AUDIO_OUTPUT_DIR"], exist_ok=True)
                    
            # Generate a timestamped filename for the transcript
            import time
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            transcript_file = os.path.join(
                os.environ.get("AUDIO_OUTPUT_DIR"), 
                f"transcript_{timestamp}.txt"
            )
            self.file_service.save_text(transcription, transcript_file)
            print(f"Transcription saved to: {transcript_file}")

        # Always print the transcription
        print(f"Transcription: {transcription}")
        
        # Always return the text 
        return transcription

    def resolve_text_source(self) -> str:
        """To resolve the input source text from config or environment.

        Returns:
            str: The resolved text content
        """
        # Prefer config text if set
        source = self.config.get("data_source")
        if not source:
            logging.warning("No source text found in config.")
            return "no text found"

        # If it's not a file path, return as is
        if not os.path.isfile(source):
            return str(source)

        # Try to read the file
        try:
            return str(FileService.read_text(source))
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
            return "No valid text to synthesize"

        # Synthesize audio
        try:
            audio_data = TextToSpeechService.synthesize(text)
        except Exception as e:
            logger.error(f"Error synthesizing audio: {e}")
            return "Error synthesizing audio"

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
