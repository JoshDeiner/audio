"""Audio playback service implementation for audio synthesis."""

import logging
from typing import Tuple, Union

import numpy as np
import sounddevice as sd

from library.bin.dependency_injection.module_loader import Injectable
from services.interfaces.audio_playback_service_interface import (
    IAudioPlaybackService,
)

logger = logging.getLogger(__name__)


@Injectable(interface=IAudioPlaybackService)
class AudioPlaybackService(IAudioPlaybackService):
    """Service for audio playback."""

    def __init__(self) -> None:
        """Initialize the audio playback service."""
        pass

    def play(
        self, audio_data: Union[np.ndarray, Tuple[np.ndarray, int]]
    ) -> None:
        """Play audio data through the default audio output.

        Args:
            audio_data: Audio data as numpy array or tuple of (audio_data, sample_rate)
        """
        try:
            # Extract audio data and sample rate if provided as a tuple
            if isinstance(audio_data, tuple) and len(audio_data) == 2:
                data, sample_rate = audio_data
            else:
                data = audio_data  # type: ignore
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
