"""Audio service interface for audio transcription tool."""

from abc import ABC, abstractmethod


class IAudioRecordingService(ABC):
    """Interface for recording audio from microphone."""

    @abstractmethod
    def record_audio(
        self,
        duration: int = 5,
        rate: int = 44100,
        chunk: int = 1024,
        channels: int = 1,
        format_type: int = 16,  # pyaudio.paInt16
    ) -> str:
        """Record audio from microphone and save to a WAV file.

        Args:
            duration: Recording duration in seconds
            rate: Sample rate in Hz 
            chunk: Buffer size
            channels: Number of audio channels (1 for mono)
            format_type: Audio format (from pyaudio constants)

        Returns:
            str: Path to the saved WAV file

        Raises:
            AudioRecordingError: If recording or saving audio fails
            FileOperationError: If input directory cannot be created or accessed
        """
        pass