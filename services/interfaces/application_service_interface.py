"""Application service interface for audio transcription tool."""

from abc import ABC, abstractmethod
from typing import Tuple


class IApplicationService(ABC):
    """Interface for the main application service that orchestrates the workflow."""

    @abstractmethod
    def run(self, duration: int = 5) -> Tuple[str, str]:
        """Run the complete audio recording and transcription workflow.

        Args:
            duration: Recording duration in seconds

        Returns:
            Tuple[str, str]: Paths to the audio file and transcript file

        Raises:
            AudioServiceError: If any part of the process fails
        """
        pass
