"""Audio recording service implementation for audio transcription tool."""

import logging
import os
import time
import wave
from typing import List

import pyaudio
from colorama import Fore, Style

from services.exceptions import AudioRecordingError, FileOperationError
from services.interfaces.audio_service_interface import IAudioRecordingService
from services.interfaces.file_service_interface import IFileService
from services.interfaces.platform_service_interface import IPlatformDetectionService

logger = logging.getLogger(__name__)


class AudioRecordingService(IAudioRecordingService):
    """Implementation for recording audio from microphone."""

    def __init__(
        self, 
        platform_service: IPlatformDetectionService, 
        file_service: IFileService
    ) -> None:
        """Initialize the audio recording service.
        
        Args:
            platform_service: Platform detection service dependency
            file_service: File service dependency
        """
        self.platform_service = platform_service
        self.file_service = file_service

    def record_audio(
        self,
        duration: int = 5,
        rate: int = 44100,
        chunk: int = 1024,
        channels: int = 1,
        format_type: int = pyaudio.paInt16,
    ) -> str:
        """Record audio from microphone and save to a WAV file.

        Args:
            duration: Recording duration in seconds
            rate: Sample rate in Hz (16kHz for Whisper)
            chunk: Buffer size
            channels: Number of audio channels (1 for mono)
            format_type: Audio format (from pyaudio constants)

        Returns:
            str: Path to the saved WAV file

        Raises:
            AudioRecordingError: If recording or saving audio fails
            FileOperationError: If input directory cannot be created or accessed
        """
        # Validate and prepare input directory
        input_dir = self._prepare_input_directory()

        # Define output file path
        output_path = os.path.join(input_dir, "voice.wav")

        # Apply platform-specific adjustments
        rate, chunk = self._apply_platform_specific_settings(rate, chunk)

        # Record and save audio
        self._record_and_save_audio(
            output_path, duration, rate, chunk, channels, format_type
        )

        return output_path

    def _prepare_input_directory(self) -> str:
        """Prepare the input directory for audio recording.

        Returns:
            str: Path to the input directory

        Raises:
            FileOperationError: If directory cannot be created or accessed
        """
        input_dir = self.file_service.sanitize_path(
            os.environ.get("AUDIO_INPUT_DIR")
        )
        if not input_dir:
            raise FileOperationError(
                "AUDIO_INPUT_DIR environment variable must be set"
            )

        try:
            return self.file_service.prepare_directory(input_dir)
        except FileOperationError as e:
            raise FileOperationError(f"Input directory error: {str(e)}")

    def _apply_platform_specific_settings(self, rate: int, chunk: int) -> tuple[int, int]:
        """Apply platform-specific audio settings.

        Args:
            rate: Original sample rate
            chunk: Original chunk size

        Returns:
            tuple[int, int]: Adjusted (rate, chunk) for the current platform
        """
        current_platform = self.platform_service.get_platform()
        logger.info(f"Running on platform: {current_platform}")

        if current_platform == "pi":
            logger.info("Running in Raspberry Pi mode")
            # Pi typically works best with default settings
            return rate, chunk

        if current_platform == "mac":
            logger.info("Running in macOS mode with adjusted parameters")
            # macOS specific settings - 48kHz is often more reliable
            return 48000, chunk

        if current_platform == "win":
            logger.info("Running in Windows mode with adjusted parameters")
            # Windows specific settings - larger chunks often work better
            return rate, 2048

        # Default for Linux and other platforms
        return rate, chunk

    def _record_and_save_audio(
        self,
        output_path: str,
        duration: int,
        rate: int,
        chunk: int,
        channels: int,
        format_type: int,
    ) -> None:
        """Record audio from microphone and save to a WAV file.

        Args:
            output_path: Path where the WAV file will be saved
            duration: Recording duration in seconds
            rate: Sample rate in Hz
            chunk: Buffer size
            channels: Number of audio channels
            format_type: Audio format (from pyaudio constants)

        Raises:
            AudioRecordingError: If recording or saving audio fails
        """
        audio = None
        stream = None

        try:
            # Initialize PyAudio
            audio = pyaudio.PyAudio()

            # Log available audio devices for debugging
            self._log_available_audio_devices(audio)

            # Countdown before recording
            self._display_recording_countdown()

            # Open audio stream
            stream = audio.open(
                format=format_type,
                channels=channels,
                rate=rate,
                input=True,
                frames_per_buffer=chunk,
            )

            # Record audio
            frames = self._capture_audio_frames(stream, chunk, rate, duration)

            # Save to WAV file
            self._save_frames_to_wav(
                output_path, audio, frames, channels, rate, format_type
            )

            logger.info(f"Audio saved to {output_path}")

        except (IOError, OSError) as e:
            logger.error(f"Error recording audio: {e}")
            raise AudioRecordingError(f"Failed to record audio: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during recording: {e}")
            raise AudioRecordingError(f"Failed to record audio: {e}")
        finally:
            # Clean up resources
            if stream:
                stream.stop_stream()
                stream.close()
            if audio:
                audio.terminate()

    def _log_available_audio_devices(self, audio: pyaudio.PyAudio) -> None:
        """Log information about available audio devices.

        Args:
            audio: PyAudio instance
        """
        logger.info("Available audio devices:")
        for i in range(audio.get_device_count()):
            try:
                device_info = audio.get_device_info_by_index(i)
                logger.info(f"Device {i}: {device_info['name']}")
            except Exception as e:
                logger.warning(f"Could not get info for device {i}: {e}")

    def _display_recording_countdown(self) -> None:
        """Display countdown before recording starts."""
        print(f"{Fore.CYAN}Recording countdown.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Recording will start in:{Style.RESET_ALL}")
        print("\n")
        for i in range(3, -1, -1):
            if i == 0:
                print(f"{Fore.MAGENTA}  {i}...{Style.RESET_ALL}")
            elif i == 1:
                print(f"{Fore.RED}  {i}...{Style.RESET_ALL}")
            elif i == 2:
                print(f"{Fore.YELLOW}  {i}...{Style.RESET_ALL}")
            else:
                print(f"{Fore.GREEN}  {i}...{Style.RESET_ALL}")
            time.sleep(1)
        print(
            f"{Fore.CYAN}Recording now! {Fore.GREEN}Speak clearly...{Style.RESET_ALL}"
        )
        print("\n")

    def _capture_audio_frames(
        self, stream: pyaudio.Stream, chunk: int, rate: int, duration: int
    ) -> List[bytes]:
        """Capture audio frames from the stream.

        Args:
            stream: PyAudio stream
            chunk: Buffer size
            rate: Sample rate
            duration: Recording duration in seconds

        Returns:
            List[bytes]: List of captured audio frames
        """
        frames = []
        total_iterations = int(rate / chunk * duration)

        for i in range(0, total_iterations):
            try:
                data = stream.read(chunk, exception_on_overflow=False)
                frames.append(data)
                # Show progress during recording
                if i % int(rate / chunk) == 0:  # Approximately every second
                    seconds_left = duration - (i // int(rate / chunk))
                    print(
                        f"{Fore.BLUE}Recording: {Fore.GREEN}{seconds_left}"
                        f"{Fore.BLUE} seconds left...{Style.RESET_ALL}"
                    )
            except Exception as e:
                logger.error(f"Error reading from stream: {e}")
                # Create some silent data to maintain timing
                frames.append(b"\x00" * chunk)

        # Ensure we display zero seconds at the end
        print(
            f"{Fore.BLUE}Recording: {Fore.GREEN}0"
            f"{Fore.BLUE} seconds left...{Style.RESET_ALL}"
        )

        return frames

    def _save_frames_to_wav(
        self,
        output_path: str,
        audio: pyaudio.PyAudio,
        frames: List[bytes],
        channels: int,
        rate: int,
        format_type: int,
    ) -> None:
        """Save audio frames to a WAV file.

        Args:
            output_path: Path where the WAV file will be saved
            audio: PyAudio instance
            frames: List of audio frames
            channels: Number of audio channels
            rate: Sample rate
            format_type: Audio format

        Raises:
            AudioRecordingError: If saving the file fails
        """
        try:
            with wave.open(output_path, "wb") as wf:
                wf.setnchannels(channels)
                wf.setsampwidth(audio.get_sample_size(format_type))
                wf.setframerate(rate)
                wf.writeframes(b"".join(frames))
        except (IOError, OSError) as e:
            logger.error(f"Error saving WAV file: {e}")
            raise AudioRecordingError(f"Failed to save audio file: {e}")
        except Exception as e:
            logger.error(f"Unexpected error saving WAV file: {e}")
            raise AudioRecordingError(f"Failed to save audio file: {e}")