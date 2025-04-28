"""Audio playback service interface for audio synthesis."""

from abc import ABC, abstractmethod
from typing import Tuple, Union

import numpy as np


class IAudioPlaybackService(ABC):
    """Interface for audio playback."""

    @abstractmethod
    def play(
        self, audio_data: Union[np.ndarray, Tuple[np.ndarray, int]]
    ) -> None:
        """Play audio data through the default audio output.

        Args:
            audio_data: Audio data as numpy array or tuple of (audio_data, sample_rate)
        """
        pass
