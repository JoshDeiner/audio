"""Text to speech service implementation for audio synthesis."""

import io
import logging
import os
import tempfile
from typing import Optional, Tuple

import numpy as np
import soundfile as sf
from gtts import gTTS

from library.bin.dependency_injection.module_loader import Injectable
from services.interfaces.text_to_speech_service_interface import (
    ITextToSpeechService,
)

logger = logging.getLogger(__name__)


@Injectable(interface=ITextToSpeechService)
class TextToSpeechService(ITextToSpeechService):
    """Service for text-to-speech synthesis."""

    def __init__(self) -> None:
        """Initialize the text-to-speech service."""
        pass

    def synthesize(
        self, text: str, voice: Optional[str] = None
    ) -> Tuple[np.ndarray, int]:
        """Synthesize text to audio using text-to-speech.

        Args:
            text: The text to synthesize
            voice: Optional voice identifier to use (language code for gTTS, e.g., 'en', 'fr', etc.)

        Returns:
            Tuple[np.ndarray, int]: Audio data as numpy array and sample rate
        """
        logger.info(
            f"Synthesizing text: {text[:30]}{'...' if len(text) > 30 else ''}"
        )

        # Use gTTS for text-to-speech synthesis
        try:
            # Default to English if no voice/language is provided
            language = voice or "en"

            # Create gTTS object
            tts = gTTS(text=text, lang=language, slow=False)

            # Save to a temporary BytesIO object
            mp3_fp = io.BytesIO()
            tts.write_to_fp(mp3_fp)
            mp3_fp.seek(0)

            # Create a temporary file to save the MP3
            with tempfile.NamedTemporaryFile(
                suffix=".mp3", delete=False
            ) as temp_file:
                temp_filename = temp_file.name
                mp3_fp.seek(0)
                temp_file.write(mp3_fp.read())

            # Use soundfile to read the audio file
            audio_data, sample_rate = sf.read(temp_filename)

            # Clean up the temporary file
            os.remove(temp_filename)

            logger.info(
                f"Generated {len(audio_data)/sample_rate:.2f}s audio at {sample_rate}Hz"
            )
            return audio_data, sample_rate

        except Exception as e:
            logger.error(f"Failed to synthesize speech with gTTS: {e}")
            logger.warning("Falling back to dummy audio generation")

            # Fallback to dummy audio generation
            sample_rate = 16000
            duration = 2.0  # seconds
            t = np.linspace(
                0, duration, int(sample_rate * duration), endpoint=False
            )

            # Create a simple sine wave
            frequencies = [440, 880]
            audio_data = np.zeros_like(t)
            for freq in frequencies:
                audio_data += 0.5 * np.sin(2 * np.pi * freq * t)

            # Normalize the audio data
            audio_data = audio_data / np.max(np.abs(audio_data))

            logger.info(
                f"Generated fallback {len(audio_data)/sample_rate:.2f}s audio at {sample_rate}Hz"
            )
            return audio_data, sample_rate
