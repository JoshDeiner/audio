"""Application service implementation for audio transcription tool."""

import logging
import os
import time
from typing import Tuple

from colorama import Fore, Style

from library.bin.dependency_injection.module_loader import Injectable
from services.exceptions import AudioServiceError
from services.interfaces.application_service_interface import (
    IApplicationService,
)
from services.interfaces.audio_service_interface import IAudioRecordingService
from services.interfaces.transcription_service_interface import (
    ITranscriptionService,
)

logger = logging.getLogger(__name__)


@Injectable(interface=IApplicationService)
class ApplicationService(IApplicationService):
    """Main application service that orchestrates the workflow."""

    def __init__(
        self,
        recording_service: IAudioRecordingService,
        transcription_service: ITranscriptionService,
    ) -> None:
        """Initialize the application service with dependencies.

        Args:
            recording_service: Service for audio recording
            transcription_service: Service for audio transcription
        """
        self.recording_service = recording_service
        self.transcription_service = transcription_service

    def run(self, duration: int = 5) -> Tuple[str, str]:
        """Run the complete audio recording and transcription workflow.

        Args:
            duration: Recording duration in seconds

        Returns:
            Tuple[str, str]: Paths to the audio file and transcript file

        Raises:
            AudioServiceError: If any part of the process fails
        """
        try:
            # Record audio
            print(f"{Fore.GREEN}Recording audio...{Style.RESET_ALL}")
            audio_path = self.recording_service.record_audio(duration=duration)
            logger.info(f"Audio recording complete. Saved to {audio_path}")

            # Transcribe the audio
            transcription = self.transcription_service.transcribe_audio(
                audio_path
            )
            print(
                f"\n{Fore.GREEN}Transcription:{Style.RESET_ALL}\n{transcription}\n"
            )

            # Get the path to the saved transcription
            transcript_path = os.path.join(
                os.environ.get("AUDIO_OUTPUT_DIR", "output"),
                f"voice_{time.strftime('%Y%m%d-%H%M%S')}.txt",
            )

            print(
                f"{Fore.CYAN}Transcription saved to: "
                f"{Fore.YELLOW}{transcript_path}{Style.RESET_ALL}"
            )

            return audio_path, transcript_path

        except AudioServiceError as e:
            logger.error(f"Audio service error: {e}")
            print(f"\n{Fore.RED}Error: {e}{Style.RESET_ALL}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            print(f"\n{Fore.RED}Unexpected error: {e}{Style.RESET_ALL}")
            raise AudioServiceError(f"Application error: {str(e)}")
