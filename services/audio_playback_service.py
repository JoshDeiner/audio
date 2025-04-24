"""Audio playback service for audio synthesis."""
import logging
from typing import Tuple, Union

import numpy as np
import sounddevice as sd

logger = logging.getLogger(__name__)


class AudioPlaybackService:
    """Service for audio playback."""

    @staticmethod
    def play(audio_data: Union[np.ndarray, Tuple[np.ndarray, int]]) -> None:
        """Play audio data through the default audio output.

        Args:
            audio_data: Audio data as numpy array or tuple of (audio_data, sample_rate)
        """
        try:
            # Extract audio data and sample rate if provided as a tuple
            if isinstance(audio_data, tuple) and len(audio_data) == 2:
                data, sample_rate = audio_data
            else:
                data = audio_data
                sample_rate = 16000  # Default sample rate

            logger.info(
                f"Playing audio: {len(data)/sample_rate:.2f}s at {sample_rate}Hz"
            )

            # Play audio using sounddevice
            sd.play(data, sample_rate)
            sd.wait()  # Wait until audio playback is done
            logger.info("Audio playback completed")

        except Exception as e:
            logger.error(f"Error playing audio: {e}")
            print(f"Error playing audio: {e}")
