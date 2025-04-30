"""Asynchronous state machine for audio input/output loops.

This module provides an asynchronous state machine that cycles between 
listening (speech-to-text) and speaking (text-to-speech) states.
"""

import asyncio
import enum
import logging
from typing import Dict, Any, Optional

from services.interfaces.audio_service_interface import IAudioRecordingService
from services.interfaces.transcription_service_interface import ITranscriptionService
from services.text_to_speech_service import TextToSpeechService
from services.audio_playback_service import AudioPlaybackService
from services.interfaces.configuration_manager_interface import IConfigurationManager

logger = logging.getLogger(__name__)


class MachineState(enum.Enum):
    """Enum defining the possible states of the audio state machine."""
    LISTENING = "listening"
    SPEAKING = "speaking"
    WAITING = "waiting"
    STOPPED = "stopped"


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
    
    def __init__(
        self,
        config: Dict[str, Any],
        audio_service: IAudioRecordingService,
        transcription_service: ITranscriptionService,
        config_manager: IConfigurationManager,
        cycles: int = 2
    ) -> None:
        """Initialize the state machine.
        
        Args:
            config: Configuration dictionary
            audio_service: Service for audio recording
            transcription_service: Service for audio transcription
            config_manager: Configuration manager
            cycles: Number of listen/speak cycles to complete (must be even and > 0)
        
        Raises:
            ValueError: If cycles is not an even number or is less than or equal to zero
        """
        # Validate that cycles is an even number greater than zero
        if cycles <= 0:
            raise ValueError("Number of cycles must be greater than zero")
        if cycles % 2 != 0:
            logger.warning(f"Requested {cycles} cycles, but cycles must be even for balanced listen/speak")
            # Round up to the next even number
            cycles = cycles + (cycles % 2)
            logger.info(f"Adjusted to {cycles} cycles")
        
        self.config = config
        self.audio_service = audio_service
        self.transcription_service = transcription_service
        self.config_manager = config_manager
        
        # Set up environment variables needed for audio recording
        self._setup_environment()
        
        self.current_state = MachineState.LISTENING
        self.cycles_completed = 0
        self.cycles_target = cycles
        self.text_result = ""
        
    def _setup_environment(self) -> None:
        """Set up required environment variables for audio services."""
        import os
        
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
        """Run the state machine until it reaches the STOPPED state."""
        while self.current_state != MachineState.STOPPED:
            if self.current_state == MachineState.LISTENING:
                await self._handle_listening_state()
            elif self.current_state == MachineState.SPEAKING:
                await self._handle_speaking_state()
            elif self.current_state == MachineState.WAITING:
                await self._handle_waiting_state()
                
            logger.info(f"State transition: {self.current_state.value}")
            
        logger.info(f"State machine stopped after {self.cycles_completed} cycles")
    
    async def _handle_listening_state(self) -> None:
        """Handle the LISTENING state.
        
        Records audio from the microphone and transcribes it.
        Transitions to the SPEAKING state after completion.
        """
        try:
            # Record audio from microphone
            logger.info("Recording audio...")
            audio_path = await asyncio.to_thread(
                self.audio_service.record_audio,
                duration=self.config.get("duration", 5)
            )
            
            # Transcribe the audio
            logger.info("Transcribing audio...")
            self.text_result = await asyncio.to_thread(
                self.transcription_service.transcribe_audio,
                audio_path,
                model_size=self.config.get("model"),
                language=self.config.get("language")
            )
            
            logger.info(f"Transcription: {self.text_result}")
            
            # Transition to SPEAKING state
            self.current_state = MachineState.SPEAKING
            
        except Exception as e:
            logger.error(f"Error in LISTENING state: {e}")
            # On error, still transition to speaking but with error message
            self.text_result = "I couldn't understand what you said."
            self.current_state = MachineState.SPEAKING
    
    async def _handle_speaking_state(self) -> None:
        """Handle the SPEAKING state.
        
        Synthesizes and plays the stored text.
        Increments cycle counter and either transitions to STOPPED or back to LISTENING.
        """
        try:
            # Generate a response (simple echo in this implementation)
            response = f"I heard you say: {self.text_result}"
            
            # Synthesize and play audio
            logger.info(f"Synthesizing response: {response}")
            
            # Use direct static methods since we don't know the config manager implementation
            audio_data = await asyncio.to_thread(
                TextToSpeechService.synthesize,
                response
            )
            
            # Play the synthesized audio
            await asyncio.to_thread(
                AudioPlaybackService.play,
                audio_data
            )
            
            # Increment cycle counter
            self.cycles_completed += 1
            
            # Check if we've reached the target number of cycles
            if self.cycles_completed >= self.cycles_target:
                logger.info(f"Completed {self.cycles_completed}/{self.cycles_target} cycles")
                self.current_state = MachineState.STOPPED
            else:
                # Optionally transition to WAITING state instead of directly to LISTENING
                self.current_state = MachineState.WAITING
                
        except Exception as e:
            logger.error(f"Error in SPEAKING state: {e}")
            # On error, still progress to next state
            self.cycles_completed += 1
            if self.cycles_completed >= self.cycles_target:
                self.current_state = MachineState.STOPPED
            else:
                self.current_state = MachineState.WAITING
    
    async def _handle_waiting_state(self) -> None:
        """Handle the WAITING state.
        
        Pauses briefly before transitioning to LISTENING state.
        """
        # Pause for a short duration
        await asyncio.sleep(0.1)
        
        # Transition to LISTENING state
        self.current_state = MachineState.LISTENING