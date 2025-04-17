#!/usr/bin/env python3
import os
import wave
import pyaudio
import logging
import time
import platform
import sys
from faster_whisper import WhisperModel
from colorama import Fore, Style, init
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize colorama with strip=False for compatibility with Docker/TTY
init(strip=False)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def get_platform():
    """Detect platform - handle special cases"""
    # Check for audio driver override first
    audio_driver = os.environ.get("AUDIO_DRIVER")
    if audio_driver:
        logger.info(f"Using audio driver from environment: {audio_driver}")
        if audio_driver == "pulse":
            return "pulse"
        elif audio_driver == "alsa":
            return "alsa"
    
    # Check for platform override
    env_platform = os.environ.get("PLATFORM")
    if env_platform:
        return env_platform.lower()
    
    # Auto-detect if not specified
    sys_platform = platform.system().lower()
    
    # Platform-specific detection
    if sys_platform == "linux":
        # Check if running on Pi
        if os.path.exists("/proc/device-tree/model"):
            try:
                with open("/proc/device-tree/model") as f:
                    model = f.read()
                    if "raspberry pi" in model.lower():
                        return "pi"
            except:
                pass
        
        # Check for pulseaudio
        try:
            if os.path.exists("/usr/bin/pulseaudio") or os.path.exists("/bin/pulseaudio"):
                return "pulse"
        except:
            pass
        
        return "linux"
    elif sys_platform == "darwin":
        return "mac"
    elif "win" in sys_platform:
        return "win"
    
    return sys_platform

def record_audio(duration=5, rate=44100, chunk=1024, channels=1, format_type=pyaudio.paInt16):
    """
    Record audio from microphone and save to a WAV file.
    
    Args:
        duration (int): Recording duration in seconds
        rate (int): Sample rate in Hz (16kHz for Whisper)
        chunk (int): Buffer size
        channels (int): Number of audio channels (1 for mono)
        format_type: Audio format (from pyaudio constants)
        
    Returns:
        str: Path to the saved WAV file
    """
    # Get the input directory from environment variable
    input_dir = os.environ.get("AUDIO_INPUT_DIR")
    if not input_dir:
        raise ValueError("AUDIO_INPUT_DIR environment variable must be set")
    
    # Try to create directory if it doesn't exist (for bind mounts)
    if not os.path.isdir(input_dir):
        try:
            os.makedirs(input_dir, exist_ok=True)
            logger.info(f"Created input directory: {input_dir}")
        except Exception as e:
            logger.error(f"Failed to create input directory: {e}")
            raise FileNotFoundError(f"Input directory does not exist: {input_dir}")
    
    # Define output file path
    output_path = os.path.join(input_dir, "voice.wav")
    
    # Platform-specific adjustments
    current_platform = get_platform()
    logger.info(f"Running on platform: {current_platform}")
    
    # Platform-specific logic
    if current_platform == "pi":
        logger.info("Running in Raspberry Pi mode")
        # Pi typically works best with default settings
        pass
    elif current_platform == "osx":
        logger.info("Running in macOS mode with adjusted parameters")
        # macOS specific settings
        # Using 48kHz on macOS is often more reliable
        rate = 48000
    elif current_platform == "win":
        logger.info("Running in Windows mode with adjusted parameters")
        # Windows specific settings
        # Some Windows systems work better with larger chunks
        chunk = 2048
    
    try:
        # Initialize PyAudio
        audio = pyaudio.PyAudio()
        
        # Print available devices for debugging
        logger.info("Available audio devices:")
        for i in range(audio.get_device_count()):
            try:
                device_info = audio.get_device_info_by_index(i)
                logger.info(f"Device {i}: {device_info['name']}")
            except:
                logger.warning(f"Could not get info for device {i}")
        
        # Countdown before recording
        print('\n')
        print(f"{Fore.CYAN}Recording countdown.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Recording will start in:{Style.RESET_ALL}")
        print('\n')
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
        print(f"{Fore.CYAN}Recording now! {Fore.GREEN}Speak clearly...{Style.RESET_ALL}")
        print('\n')
        
        # Try to find a working input device
        device_index = None
        for i in range(audio.get_device_count()):
            try:
                dev_info = audio.get_device_info_by_index(i)
                if dev_info['maxInputChannels'] > 0:
                    logger.info(f"Using input device: {dev_info['name']}")
                    device_index = i
                    break
            except:
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
                frames_per_buffer=chunk
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
                frames_per_buffer=chunk
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
                    print(f"{Fore.BLUE}Recording: {Fore.GREEN}{seconds_left}{Fore.BLUE} seconds left...{Style.RESET_ALL}")
            except Exception as e:
                logger.error(f"Error reading from stream: {e}")
                # Create some silent data to maintain timing
                frames.append(b'\x00' * chunk * channels * audio.get_sample_size(format_type))
        
        # Ensure we display zero seconds at the end
        print(f"{Fore.BLUE}Recording: {Fore.GREEN}0{Fore.BLUE} seconds left...{Style.RESET_ALL}")
        
        # Stop and close the stream
        stream.stop_stream()
        stream.close()
        audio.terminate()
        
        print('\n')
        logger.info("Recording finished.")
        
        # Save to WAV file
        with wave.open(output_path, 'wb') as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(audio.get_sample_size(format_type))
            wf.setframerate(rate)
            wf.writeframes(b''.join(frames))
        
        logger.info(f"Saved to {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Error recording audio: {e}")
        # Create an empty file in case of error
        with open(output_path, 'wb') as f:
            pass
        logger.info(f"Created empty file: {output_path}")
        return output_path

def transcribe_audio(audio_file_path, model_size=None):
    """
    Transcribe audio file using faster-whisper model.
    
    Args:
        audio_file_path (str): Path to the audio file to transcribe
        model_size (str): Whisper model size (tiny, base, small, medium, large)
        
    Returns:
        str: Transcribed text
    """
    try:
        # Get model size from environment variable or use default
        if model_size is None:
            model_size = os.environ.get("WHISPER_MODEL", "tiny").lower()  # Convert to lowercase
        
        # Get compute type from environment or use default
        compute_type = os.environ.get("WHISPER_COMPUTE_TYPE", "float32")
        
        # Get device from environment or use default (cuda if available, otherwise cpu)
        device = os.environ.get("WHISPER_DEVICE", "auto")
        
        logger.info(f"Loading faster-whisper model: {model_size} (device: {device}, compute_type: {compute_type})")
        model = WhisperModel(model_size, device=device, compute_type=compute_type)
        
        logger.info(f"Transcribing audio file: {audio_file_path}")
        print(f"{Fore.CYAN}Transcribing audio...{Style.RESET_ALL}")
        
        # Transcribe the audio file
        # The faster-whisper API returns segments and info
        segments, info = model.transcribe(audio_file_path, beam_size=5)
        
        # Combine all segments into a single transcription
        transcription = " ".join([segment.text for segment in segments])
        
        logger.info(f"Transcription complete (detected language: {info.language}, probability: {info.language_probability:.2f})")
        return transcription
    
    except Exception as e:
        logger.error(f"Error transcribing audio: {e}")
        return f"Error during transcription: {str(e)}"

def save_transcription(transcription_text):
    """
    Save transcription to a text file in the output directory.
    
    Args:
        transcription_text (str): The transcribed text to save
        
    Returns:
        str: Path to the saved transcription file
    """
    # Get the output directory from environment variable
    output_dir = os.environ.get("AUDIO_OUTPUT_DIR")
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
        with open(output_path, 'w') as f:
            f.write(transcription_text)
        
        logger.info(f"Transcription saved to {output_path}")
        return output_path
    
    except Exception as e:
        logger.error(f"Error saving transcription: {e}")
        raise

def main():
    """Entry point when script is run directly."""
    try:
        # Record audio
        audio_path = record_audio()
        logger.info(f"Audio recording complete. Saved to {audio_path}")
        
        # Transcribe the audio
        transcription = transcribe_audio(audio_path)
        print(f"\n{Fore.GREEN}Transcription:{Style.RESET_ALL}\n{transcription}\n")
        
        # Save the transcription
        transcript_path = save_transcription(transcription)
        print(f"{Fore.CYAN}Transcription saved to: {Fore.YELLOW}{transcript_path}{Style.RESET_ALL}")
        
        return audio_path, transcript_path
    
    except Exception as e:
        logger.error(f"Error in main function: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
