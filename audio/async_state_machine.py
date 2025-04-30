"""Asynchronous state machine for audio input/output loops.

This module provides an asynchronous state machine that cycles between
listening (speech-to-text) and speaking (text-to-speech) states.

Author: Claude Code
Created: 2025-04-30
"""

import asyncio
import enum
import logging
import os
from typing import Any, Dict, Final

from services.audio_playback_service import AudioPlaybackService
from services.exceptions import AudioServiceError
from services.interfaces.audio_service_interface import IAudioRecordingService
from services.interfaces.configuration_manager_interface import (
    IConfigurationManager,
)
from services.interfaces.transcription_service_interface import (
    ITranscriptionService,
)
from services.text_to_speech_service import TextToSpeechService

logger = logging.getLogger(__name__)


class MachineState(enum.Enum):
    """Enum defining the possible states of the audio state machine."""

    LISTENING = "listening"
    SPEAKING = "speaking"
    WAITING = "waiting"
    STOPPED = "stopped"


class StateMachineError(Exception):
    """Base exception for state machine errors."""


class CycleConfigurationError(StateMachineError):
    """Raised when cycle configuration is invalid."""


class StateTransitionError(StateMachineError):
    """Raised when there is an error during state transition."""


class AsyncAudioStateMachine:
    """Asynchronous state machine for handling audio input/output cycles.

    This class implements a state machine that cycles between recording audio,
    transcribing it, generating a response, and speaking the response.

    Attributes:
        config: Configuration settings for the state machine
        audio_service: Service for recording audio
        transcription_service: Service for transcribing audio
        config_manager: Service for managing configuration
        current_state: Current state of the state machine
        cycles_completed: Number of input/output cycles completed
        cycles_target: Total number of cycles to run before stopping
        text_result: Text result from the most recent listening state
    """

    # Constants
    DEFAULT_DURATION: Final[int] = 5
    DEFAULT_CYCLES: Final[int] = 2
    DEFAULT_WAIT_DURATION: Final[float] = 0.1
    ERROR_MESSAGE: Final[str] = "I couldn't understand what you said."

    def __init__(
        self,
        config: Dict[str, Any],
        audio_service: IAudioRecordingService,
        transcription_service: ITranscriptionService,
        config_manager: IConfigurationManager,
        cycles: int = DEFAULT_CYCLES,
    ) -> None:
        """Initialize the state machine.

        Args:
            config: Configuration dictionary
            audio_service: Service for audio recording
            transcription_service: Service for audio transcription
            config_manager: Configuration manager
            cycles: Number of listen/speak cycles to complete (must be even and > 0)

        Raises:
            CycleConfigurationError: If cycles is not a valid number
        """
        # Guard clause: Validate that cycles is a positive number
        if cycles <= 0:
            raise CycleConfigurationError("Number of cycles must be greater than zero")

        # Ensure even number of cycles for balanced listen/speak
        if cycles % 2 != 0:
            logger.warning(
                f"Requested {cycles} cycles, but cycles must be even for balanced listen/speak"
            )
            # Round up to the next even number
            cycles = cycles + (cycles % 2)
            logger.info(f"Adjusted to {cycles} cycles")

        self.config = config
        self.audio_service = audio_service
        self.transcription_service = transcription_service
        self.config_manager = config_manager
        self.cycles_target = cycles

        # Initialize state machine state
        self.current_state = MachineState.LISTENING
        self.cycles_completed = 0
        self.text_result = ""

        # Set up environment variables needed for audio recording
        self._setup_environment()

    def _setup_environment(self) -> None:
        """Set up required environment variables for audio services.

        Creates input and output directories if they don't exist and
        sets the appropriate environment variables.
        """
        # Ensure input directory exists
        input_dir = os.path.join(os.getcwd(), "input")
        os.makedirs(input_dir, exist_ok=True)
        os.environ["AUDIO_INPUT_DIR"] = input_dir
        logger.info(f"Set AUDIO_INPUT_DIR: {input_dir}")

        # Ensure output directory exists
        output_dir = os.path.join(os.getcwd(), "output")
        os.makedirs(output_dir, exist_ok=True)
        os.environ["AUDIO_OUTPUT_DIR"] = output_dir
        logger.info(f"Set AUDIO_OUTPUT_DIR: {output_dir}")

    async def run(self) -> None:
        """Run the state machine until it reaches the STOPPED state.

        This method manages the state transitions according to the current state
        until the state machine reaches the STOPPED state.
        """
        while self.current_state != MachineState.STOPPED:
            # Use match-case for cleaner state handling
            match self.current_state:
                case MachineState.LISTENING:
                    await self._handle_listening_state()
                case MachineState.SPEAKING:
                    await self._handle_speaking_state()
                case MachineState.WAITING:
                    await self._handle_waiting_state()
                case _:
                    logger.warning(f"Unhandled state: {self.current_state}")
                    self.current_state = MachineState.STOPPED

            logger.info(f"State transition: {self.current_state.value}")

        logger.info(
            f"State machine stopped after {self.cycles_completed} cycles"
        )

    async def _handle_listening_state(self) -> None:
        """Handle the LISTENING state.

        Records audio from the microphone and transcribes it.
        Transitions to the SPEAKING state after completion.

        Exceptions are caught and logged, with a fallback error message.
        """
        try:
            # Record audio from microphone
            logger.info("Recording audio...")
            recording_duration = self.config.get("duration", self.DEFAULT_DURATION)

            audio_path = await asyncio.to_thread(
                self.audio_service.record_audio,
                duration=recording_duration,
            )

            # Transcribe the audio
            logger.info("Transcribing audio...")
            self.text_result = await asyncio.to_thread(
                self.transcription_service.transcribe_audio,
                audio_path,
                model_size=self.config.get("model"),
                language=self.config.get("language"),
            )

            logger.info(f"Transcription: {self.text_result}")

        except AudioServiceError as e:
            logger.error(f"Audio service error in LISTENING state: {e}")
            self.text_result = self.ERROR_MESSAGE
        except Exception as e:
            logger.error(f"Unexpected error in LISTENING state: {e}")
            self.text_result = self.ERROR_MESSAGE
        finally:
            # Always transition to SPEAKING state
            self.current_state = MachineState.SPEAKING

    async def _handle_speaking_state(self) -> None:
        """Handle the SPEAKING state.

        Synthesizes and plays the stored text.
        Increments cycle counter and either transitions to STOPPED or WAITING.

        Exceptions are caught and logged, with appropriate state transitions.
        """
        try:
            # Generate a response (simple echo in this implementation)
            response = f"I heard you say: {self.text_result}"

            # Synthesize and play audio
            logger.info(f"Synthesizing response: {response}")

            # Use asyncio.to_thread for CPU-intensive operations
            audio_data = await asyncio.to_thread(
                TextToSpeechService.synthesize, response
            )

            # Play the synthesized audio
            await asyncio.to_thread(AudioPlaybackService.play, audio_data)

        except AudioServiceError as e:
            logger.error(f"Audio service error in SPEAKING state: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in SPEAKING state: {e}")
        finally:
            # Always increment cycle counter
            self.cycles_completed += 1

            # Determine next state based on cycle count
            if self.cycles_completed >= self.cycles_target:
                logger.info(
                    f"Completed {self.cycles_completed}/{self.cycles_target} cycles"
                )
                self.current_state = MachineState.STOPPED
            else:
                # Transition to WAITING state before next listening cycle
                self.current_state = MachineState.WAITING

    async def _handle_waiting_state(self) -> None:
        """Handle the WAITING state.

        Pauses briefly before transitioning to LISTENING state.
        This provides a natural break in the conversation flow.
        """
        # Pause for a short duration
        wait_duration = self.config.get("wait_duration", self.DEFAULT_WAIT_DURATION)
        await asyncio.sleep(wait_duration)

        # Transition to LISTENING state
        self.current_state = MachineState.LISTENING
