"""Text to speech service interface for audio synthesis."""

from abc import ABC, abstractmethod
from typing import Optional, Tuple

import numpy as np


class ITextToSpeechService(ABC):
    """Interface for text-to-speech synthesis."""

    @abstractmethod
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
        pass
