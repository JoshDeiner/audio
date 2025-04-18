#!/usr/bin/env python3
"""Audio transcription module using faster-whisper.

This module provides functionality to record audio from a microphone
and transcribe it using the faster-whisper model.
"""
import logging
import os
import platform
import sys
import time
import wave
from typing import Dict, List, Optional, Tuple, Union

import pyaudio  # type: ignore
from colorama import Fore, Style, init  # type: ignore
from dotenv import load_dotenv
from faster_whisper import WhisperModel  # type: ignore

# Load environment variables from .env file
load_dotenv()

# Initialize colorama with strip=False for compatibility with Docker/TTY
init(strip=False)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def sanitize_path(path: Optional[str]) -> str:
    """Sanitize file path to prevent directory traversal.

    Args:
        path: The file path to sanitize

    Returns:
        A sanitized version of the path
    """
    if not path:
        return ""
    return os.path.normpath(os.path.join("/", path)).lstrip("/")


def get_platform() -> str:
    """Detect platform and audio driver configuration.
    
    This function determines the platform or audio driver to use for audio recording.
    It checks for environment variables first, then falls back to auto-detection.
    
    Returns:
        str: Identifier for the platform or audio driver. Possible values:
            - "pulse": PulseAudio driver
            - "alsa": ALSA driver
            - "pi": Raspberry Pi
            - "linux": Generic Linux
            - "mac": macOS
            - "win": Windows
            - Any other platform string as returned by platform.system()
    
    Raises:
        No exceptions are raised as this function handles all errors internally.
    """
    # Check for environment variable overrides first
    platform_from_env = _get_platform_from_env()
    if platform_from_env:
        return platform_from_env
        
    # Auto-detect if not specified in environment
    return _detect_platform_automatically()


def _get_platform_from_env() -> str:
    """Get platform or audio driver from environment variables.
    
    Checks environment variables in order of priority:
    1. AUDIO_DRIVER - For specific audio driver configuration
    2. PLATFORM - For explicit platform specification
    
    Returns:
        str: Platform or audio driver identifier, or empty string if not found
    """
    # Check for audio driver override (highest priority)
    audio_driver = _get_valid_audio_driver_from_env()
    if audio_driver:
        return audio_driver
    
    # Check for platform override (second priority)
    return _get_platform_override_from_env()


def _get_valid_audio_driver_from_env() -> str:
    """Get valid audio driver from environment variable.
    
    Returns:
        str: Valid audio driver name or empty string
    """
    audio_driver = os.environ.get("AUDIO_DRIVER", "").strip()
    
    # Return early if no audio driver specified
    if not audio_driver:
        return ""
        
    logger.info(f"Using audio driver from environment: {audio_driver}")
    audio_driver = audio_driver.lower()
    
    # Return early if not a recognized audio driver
    if audio_driver not in ("pulse", "alsa"):
        logger.debug(f"Unrecognized audio driver: {audio_driver}")
        return ""
        
    return audio_driver


def _get_platform_override_from_env() -> str:
    """Get platform override from environment variable.
    
    Returns:
        str: Platform name or empty string
    """
    env_platform = os.environ.get("PLATFORM", "")
    if not env_platform:
        return ""
        
    return env_platform.lower()


def _detect_platform_automatically() -> str:
    """Auto-detect platform based on system information.
    
    Returns:
        str: Detected platform identifier
    """
    sys_platform = platform.system().lower()
    
    if sys_platform == "linux":
        return _detect_linux_platform()
    
    if sys_platform == "darwin":
        return "mac"
        
    if sys_platform.startswith("win"):
        return "win"
        
    return sys_platform


def _detect_linux_platform() -> str:
    """Detect specific Linux platform or audio driver.
    
    Helper function to determine the specific Linux platform or audio driver.
    
    Returns:
        str: Linux platform identifier ("pi", "pulse", or "linux")
    """
    # Try to detect Raspberry Pi first
    pi_platform = _check_for_raspberry_pi()
    if pi_platform:
        return pi_platform
        
    # Then check for PulseAudio
    pulse_platform = _check_for_pulseaudio()
    if pulse_platform:
        return pulse_platform
        
    # Default to generic Linux
    return "linux"


def _check_for_raspberry_pi() -> str:
    """Check if running on a Raspberry Pi.
    
    Returns:
        str: "pi" if running on Raspberry Pi, empty string otherwise
    """
    pi_model_path = "/proc/device-tree/model"
    
    if not os.path.exists(pi_model_path):
        return ""
        
    try:
        with open(pi_model_path) as f:
            model = f.read().lower()
            if "raspberry pi" not in model:
                return ""
            return "pi"
    except (IOError, OSError) as e:
        logger.debug(f"Error reading Raspberry Pi model: {e}")
        return ""


def _check_for_pulseaudio() -> str:
    """Check if PulseAudio is installed.
    
    Returns:
        str: "pulse" if PulseAudio is installed, empty string otherwise
    """
    pulse_paths = ["/usr/bin/pulseaudio", "/bin/pulseaudio"]
    
    try:
        if not any(os.path.exists(path) for path in pulse_paths):
            return ""
        return "pulse"
    except (IOError, OSError) as e:
        logger.debug(f"Error checking for PulseAudio: {e}")
        return ""


def validate_audio_file(file_path: str) -> bool:
    """Validate that the file is a proper audio file.

    Args:
        file_path: Path to the audio file to validate

    Returns:
        bool: True if the file is a valid WAV file, False otherwise
    """
    if not os.path.exists(file_path):
        logger.error(f"Audio file not found: {file_path}")
        return False
        
    try:
        with wave.open(file_path, "rb") as wf:
            # Check basic WAV file properties
            if wf.getnchannels() < 1:
                logger.error(f"Invalid audio channels in {file_path}")
                return False
                
            if wf.getsampwidth() < 1:
                logger.error(f"Invalid sample width in {file_path}")
                return False
                
            if wf.getframerate() < 1:
                logger.error(f"Invalid frame rate in {file_path}")
                return False
                
            return True
    except wave.Error as e:
        logger.error(f"WAV file format error: {e}")
        return False
    except (IOError, OSError) as e:
        logger.error(f"File I/O error during audio validation: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during audio validation: {e}")
        return False


def record_audio(
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
        ValueError: If required environment variables are not set
        FileNotFoundError: If input directory cannot be created or accessed
        IOError: If there's an error recording or saving audio
    """
    # Validate and prepare input directory
    input_dir = _prepare_input_directory()
    
    # Define output file path
    output_path = os.path.join(input_dir, "voice.wav")
    
    # Apply platform-specific adjustments
    rate, chunk = _apply_platform_specific_settings(rate, chunk)
    
    # Record and save audio
    _record_and_save_audio(output_path, duration, rate, chunk, channels, format_type)
    
    return output_path


def _prepare_input_directory() -> str:
    """Prepare the input directory for audio recording.
    
    Returns:
        str: Path to the input directory
        
    Raises:
        ValueError: If AUDIO_INPUT_DIR environment variable is not set
        FileNotFoundError: If directory cannot be created or accessed
    """
    input_dir = sanitize_path(os.environ.get("AUDIO_INPUT_DIR"))
    if not input_dir:
        raise ValueError("AUDIO_INPUT_DIR environment variable must be set")

    # Try to create directory if it doesn't exist
    if not os.path.isdir(input_dir):
        try:
            os.makedirs(input_dir, exist_ok=True)
            logger.info(f"Created input directory: {input_dir}")
        except (IOError, OSError) as e:
            logger.error(f"Failed to create input directory: {e}")
            raise FileNotFoundError(f"Input directory does not exist: {input_dir}")

    return input_dir


def _apply_platform_specific_settings(rate: int, chunk: int) -> Tuple[int, int]:
    """Apply platform-specific audio settings.
    
    Args:
        rate: Original sample rate
        chunk: Original chunk size
        
    Returns:
        Tuple[int, int]: Adjusted (rate, chunk) for the current platform
    """
    current_platform = get_platform()
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
        IOError: If there's an error recording or saving audio
    """
    audio = None
    stream = None
    
    try:
        # Initialize PyAudio
        audio = pyaudio.PyAudio()
        
        # Log available audio devices for debugging
        _log_available_audio_devices(audio)
        
        # Countdown before recording
        _display_recording_countdown()
        
        # Open audio stream
        stream = audio.open(
            format=format_type,
            channels=channels,
            rate=rate,
            input=True,
            frames_per_buffer=chunk,
        )
        
        # Record audio
        frames = _capture_audio_frames(stream, chunk, rate, duration)
        
        # Save to WAV file
        _save_frames_to_wav(output_path, audio, frames, channels, rate, format_type)
        
        logger.info(f"Audio saved to {output_path}")
        
    except (IOError, OSError) as e:
        logger.error(f"Error recording audio: {e}")
        raise IOError(f"Failed to record audio: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during recording: {e}")
        raise IOError(f"Failed to record audio: {e}")
    finally:
        # Clean up resources
        if stream:
            stream.stop_stream()
            stream.close()
        if audio:
            audio.terminate()


def _log_available_audio_devices(audio: pyaudio.PyAudio) -> None:
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


def _display_recording_countdown() -> None:
    """Display countdown before recording starts."""
    for i in range(3, 0, -1):
        print(f"{Fore.YELLOW}Recording will start in {i}...{Style.RESET_ALL}")
        time.sleep(1)
    print(f"{Fore.RED}Recording...{Style.RESET_ALL}")


def _capture_audio_frames(
    stream: pyaudio.Stream, chunk: int, rate: int, duration: int
) -> list:
    """Capture audio frames from the stream.
    
    Args:
        stream: PyAudio stream
        chunk: Buffer size
        rate: Sample rate
        duration: Recording duration in seconds
        
    Returns:
        list: List of captured audio frames
    """
    frames = []
    for _ in range(0, int(rate / chunk * duration)):
        data = stream.read(chunk, exception_on_overflow=False)
        frames.append(data)
    return frames


def _save_frames_to_wav(
    output_path: str,
    audio: pyaudio.PyAudio,
    frames: list,
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
        IOError: If there's an error saving the file
    """
    # Prepare WAV parameters
    wav_params = _prepare_wav_parameters(audio, channels, rate, format_type)
    
    # Join frames into a single binary blob
    audio_data = _join_audio_frames(frames)
    
    # Write to file
    _write_wav_file(output_path, wav_params, audio_data)


def _prepare_wav_parameters(
    audio: pyaudio.PyAudio, channels: int, rate: int, format_type: int
) -> Dict[str, int]:
    """Prepare WAV file parameters.
    
    Args:
        audio: PyAudio instance
        channels: Number of audio channels
        rate: Sample rate
        format_type: Audio format
        
    Returns:
        Dict[str, int]: Dictionary of WAV parameters
    """
    return {
        "channels": channels,
        "sample_width": audio.get_sample_size(format_type),
        "framerate": rate
    }


def _join_audio_frames(frames: list) -> bytes:
    """Join audio frames into a single binary blob.
    
    Args:
        frames: List of audio frame data
        
    Returns:
        bytes: Joined audio data
    """
    return b"".join(frames)


def _write_wav_file(output_path: str, wav_params: Dict[str, int], audio_data: bytes) -> None:
    """Write audio data to a WAV file.
    
    Args:
        output_path: Path where the WAV file will be saved
        wav_params: Dictionary of WAV parameters
        audio_data: Binary audio data
        
    Raises:
        IOError: If there's an error writing the file
    """
    try:
        with wave.open(output_path, "wb") as wf:
            wf.setnchannels(wav_params["channels"])
            wf.setsampwidth(wav_params["sample_width"])
            wf.setframerate(wav_params["framerate"])
            wf.writeframes(audio_data)
    except (IOError, OSError) as e:
        logger.error(f"Error saving WAV file: {e}")
        raise IOError(f"Failed to save audio file: {e}")
    except Exception as e:
        logger.error(f"Unexpected error saving WAV file: {e}")
        raise IOError(f"Failed to save audio file: {e}")
        print("\n")
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

        # Try to find a working input device
        device_index = None
        for i in range(audio.get_device_count()):
            try:
                dev_info = audio.get_device_info_by_index(i)
                if int(dev_info["maxInputChannels"]) > 0:
                    logger.info(f"Using input device: {dev_info['name']}")
                    device_index = i
                    break
            except Exception:
                continue

        # Open audio stream for recording with error handling
        logger.info("Recording started...")

        try:
            stream = audio.open(
                format=format_type,
                channels=channels,
                rate=rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=chunk,
            )
        except Exception as e:
            logger.error(f"Failed to open audio stream: {e}")
            # Fall back to default device
            logger.info("Falling back to default audio device")
            stream = audio.open(
                format=format_type,
                channels=channels,
                rate=rate,
                input=True,
                frames_per_buffer=chunk,
            )

        # Record audio data
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
                frames.append(
                    b"\x00" * chunk * channels * audio.get_sample_size(format_type)
                )

        # Ensure we display zero seconds at the end
        print(
            f"{Fore.BLUE}Recording: {Fore.GREEN}0"
            f"{Fore.BLUE} seconds left...{Style.RESET_ALL}"
        )

        # Stop and close the stream
        stream.stop_stream()
        stream.close()
        audio.terminate()

        print("\n")
        logger.info("Recording finished.")

        # Save to WAV file
        with wave.open(output_path, "wb") as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(audio.get_sample_size(format_type))
            wf.setframerate(rate)
            wf.writeframes(b"".join(frames))

        logger.info(f"Saved to {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"Error recording audio: {e}")
        # Create an empty file in case of error
        with open(output_path, "wb"):
            pass
        logger.info(f"Created empty file: {output_path}")
        return output_path


def transcribe_audio(audio_file_path: str, model_size: Optional[str] = None) -> str:
    """Transcribe audio file using faster-whisper model.

    Args:
        audio_file_path: Path to the audio file to transcribe
        model_size: Whisper model size (tiny, base, small, medium, large)

    Returns:
        str: Transcribed text or error message
    """
    # Validate input file
    if not _is_valid_audio_file(audio_file_path):
        return "Error: Invalid or corrupted audio file"
    
    # Get model configuration
    model_config = _get_whisper_model_config(model_size)
    
    # Load and run the model
    try:
        return _run_whisper_transcription(audio_file_path, model_config)
def _run_whisper_transcription(audio_file_path: str, model_config: Dict[str, str]) -> str:
    """Run the Whisper model transcription.
    
    Args:
        audio_file_path: Path to the audio file
        model_config: Model configuration dictionary
        
    Returns:
        str: Transcribed text
        
    Raises:
        Exception: If transcription fails
    """
    logger.info(f"Loading Whisper model: {model_config['model_size']}")
    logger.info(f"Using compute type: {model_config['compute_type']}")
    logger.info(f"Using device: {model_config['device']}")
    
    # Initialize the model
    model = WhisperModel(
        model_config['model_size'],
        device=model_config['device'],
        compute_type=model_config['compute_type'],
    )
    
    # Run transcription
    logger.info(f"Transcribing audio file: {audio_file_path}")
    segments, _ = model.transcribe(audio_file_path, beam_size=5)
    
    # Collect transcription segments
    transcription = ""
    for segment in segments:
        transcription += segment.text + " "
    
    # Save transcription to output file
    output_file = _save_transcription_to_file(audio_file_path, transcription)
    logger.info(f"Transcription saved to: {output_file}")
    
    return transcription.strip()


def _save_transcription_to_file(audio_file_path: str, transcription: str) -> str:
    """Save transcription to a text file.
    
    Args:
        audio_file_path: Path to the original audio file
        transcription: Transcribed text
        
    Returns:
        str: Path to the saved transcription file
        
    Raises:
        IOError: If saving fails
    """
    # Get output directory from environment or use default
    output_dir = sanitize_path(os.environ.get("AUDIO_OUTPUT_DIR", "output"))
    
    # Create output directory if it doesn't exist
    if not os.path.isdir(output_dir):
        try:
            os.makedirs(output_dir, exist_ok=True)
            logger.info(f"Created output directory: {output_dir}")
        except (IOError, OSError) as e:
            logger.error(f"Failed to create output directory: {e}")
            # Fall back to current directory
            output_dir = "."
    
    # Generate output filename based on input filename
    base_name = os.path.basename(audio_file_path)
    file_name = os.path.splitext(base_name)[0]
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    output_file = os.path.join(output_dir, f"{file_name}_{timestamp}.txt")
    
    # Save transcription to file
    try:
        with open(output_file, "w") as f:
            f.write(transcription)
        return output_file
    except (IOError, OSError) as e:
        logger.error(f"Failed to save transcription: {e}")
        raise IOError(f"Failed to save transcription: {e}")
def sanitize_path(path: Optional[str]) -> str:
    """Sanitize and normalize a file path.
    
    Args:
        path: Input path string, may be None
        
    Returns:
        str: Sanitized path or empty string if input was None
    """
    if not path:
        return ""
        
    # Expand user directory (~/...)
    path = os.path.expanduser(path)
    
    # Normalize path separators and resolve relative paths
    return os.path.normpath(path)


def main() -> None:
    """Main entry point for the transcription tool."""
    try:
        # Record audio
        print(f"{Fore.GREEN}Recording audio...{Style.RESET_ALL}")
        audio_file = record_audio(duration=5)
        
        # Transcribe audio
        print(f"{Fore.GREEN}Transcribing audio...{Style.RESET_ALL}")
        transcription = transcribe_audio(audio_file)
        
        # Print result
        print(f"\n{Fore.CYAN}Transcription:{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{transcription}{Style.RESET_ALL}\n")
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Process interrupted by user.{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}Error: {e}{Style.RESET_ALL}")
        logger.error(f"Application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
    
    # Validate model size
    valid_sizes = ["tiny", "base", "small", "medium", "large"]
    if model_size not in valid_sizes:
        logger.warning(f"Invalid model size: {model_size}. Using 'tiny' instead.")
        model_size = "tiny"
    
    # Get compute type from environment or use default
    compute_type = os.environ.get("WHISPER_COMPUTE_TYPE", "float32")
    
    # Get device from environment or use default
    device = os.environ.get("WHISPER_DEVICE", "auto")
    
    return {
        "model_size": model_size,
        "compute_type": compute_type,
        "device": device
    }

        # Get compute type from environment or use default
        compute_type = os.environ.get("WHISPER_COMPUTE_TYPE", "float32")

        # Get device from environment or use default (cuda if available, otherwise cpu)
        device = os.environ.get("WHISPER_DEVICE", "auto")

        logger.info(
            f"Loading faster-whisper model: {model_size} "
            f"(device: {device}, compute_type: {compute_type})"
        )
        model = WhisperModel(model_size, device=device, compute_type=compute_type)

        logger.info(f"Transcribing audio file: {audio_file_path}")
        print(f"{Fore.CYAN}Transcribing audio...{Style.RESET_ALL}")

        # Transcribe the audio file
        # The faster-whisper API returns segments and info
        segments, info = model.transcribe(audio_file_path, beam_size=5)

        # Combine all segments into a single transcription
        transcription = " ".join([segment.text for segment in segments])

        logger.info(
            f"Transcription complete (detected language: {info.language}, "
            f"probability: {info.language_probability:.2f})"
        )
        return transcription

    except Exception as e:
        logger.error(f"Error transcribing audio: {e}")
        return f"Error during transcription: {str(e)}"


def save_transcription(transcription_text: str) -> str:
    """Save transcription to a text file in the output directory.

    Args:
        transcription_text: The transcribed text to save

    Returns:
        Path to the saved transcription file

    Raises:
        ValueError: If required environment variables are not set
        FileNotFoundError: If output directory cannot be created or accessed
    """
    # Get the output directory from environment variable
    output_dir = sanitize_path(os.environ.get("AUDIO_OUTPUT_DIR"))
    if not output_dir:
        raise ValueError("AUDIO_OUTPUT_DIR environment variable must be set")

    # Try to create directory if it doesn't exist
    if not os.path.isdir(output_dir):
        try:
            os.makedirs(output_dir, exist_ok=True)
            logger.info(f"Created output directory: {output_dir}")
        except Exception as e:
            logger.error(f"Failed to create output directory: {e}")
            raise FileNotFoundError(f"Output directory does not exist: {output_dir}")

    # Define output file path
    output_path = os.path.join(output_dir, "transcript.txt")

    try:
        # Write transcription to file
        with open(output_path, "w") as f:
            f.write(transcription_text)

        logger.info(f"Transcription saved to {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"Error saving transcription: {e}")
        raise


def main() -> Tuple[str, str]:
    """Entry point when script is run directly.

    Returns:
        Tuple containing paths to the audio file and transcript file

    Raises:
        SystemExit: If an error occurs during execution
    """
    try:
        # Record audio
        audio_path = record_audio()
        logger.info(f"Audio recording complete. Saved to {audio_path}")

        # Transcribe the audio
        transcription = transcribe_audio(audio_path)
        print(f"\n{Fore.GREEN}Transcription:{Style.RESET_ALL}\n{transcription}\n")

        # Save the transcription
        transcript_path = save_transcription(transcription)
        print(
            f"{Fore.CYAN}Transcription saved to: "
            f"{Fore.YELLOW}{transcript_path}{Style.RESET_ALL}"
        )

        return audio_path, transcript_path

    except Exception as e:
        logger.error(f"Error in main function: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
