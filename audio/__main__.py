#!/usr/bin/env python3
"""Audio transcription module using faster-whisper.

This module provides functionality to record audio from a microphone
and transcribe it using the faster-whisper model.

It also supports transcribing existing audio files for testing and
development when recording is not possible.

The implementation follows a service-oriented architecture with clear
separation of concerns between audio recording, transcription processing,
and output management.
"""
import argparse
import logging
import os
import sys
from typing import List, Optional, Tuple, Union

from colorama import Fore, Style, init  # type: ignore
from dotenv import load_dotenv

from services.application_service import ApplicationService
from services.exceptions import AudioServiceError, FileOperationError
from services.file_transcription_service import FileTranscriptionService

# Load environment variables from .env file
load_dotenv()

# Initialize colorama with strip=False for compatibility with Docker/TTY
init(strip=False)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments.

    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Audio transcription tool using faster-whisper"
    )
    
    # Mode selection
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--record", "-r", 
        action="store_true",
        help="Record audio from microphone (default mode)"
    )
    mode_group.add_argument(
        "--file", "-f", 
        metavar="FILE",
        help="Transcribe a specific audio file"
    )
    mode_group.add_argument(
        "--dir", "-d", 
        metavar="DIR",
        help="Transcribe all WAV files in a directory"
    )
    
    # Recording options
    parser.add_argument(
        "--duration", "-t", 
        type=int, 
        default=5,
        help="Recording duration in seconds (default: 5)"
    )
    
    # Model options
    parser.add_argument(
        "--model", "-m", 
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model size (default: from .env or 'tiny')"
    )
    
    # Language option
    parser.add_argument(
        "--language", "-l",
        help="Language code to use (e.g., 'en' for English). Skips language detection."
    )
    
    # Create dummy file options
    parser.add_argument(
        "--create-dummy", "-c", 
        action="store_true",
        help="Create a dummy WAV file for testing"
    )
    parser.add_argument(
        "--dummy-text", 
        metavar="TEXT",
        help="Text to use for speech synthesis (requires gtts and librosa)"
    )
    
    return parser.parse_args()


def create_dummy_file(text: Optional[str] = None) -> str:
    """Create a dummy WAV file for testing.

    Args:
        text: Optional text for speech synthesis

    Returns:
        str: Path to the created file
    """
    input_dir = os.environ.get("AUDIO_INPUT_DIR", "input")
    os.makedirs(input_dir, exist_ok=True)
    
    if text:
        try:
            # Try to import required packages
            from gtts import gTTS
            import librosa
            import soundfile as sf
            import tempfile
            
            # Create a temporary MP3 file
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_mp3:
                temp_mp3_path = temp_mp3.name
            
            # Generate speech
            tts = gTTS(text=text, lang="en", slow=False)
            tts.save(temp_mp3_path)
            
            # Convert to WAV
            output_path = os.path.join(input_dir, "dummy_speech.wav")
            audio_data, sample_rate = librosa.load(temp_mp3_path, sr=16000)
            sf.write(output_path, audio_data, sample_rate)
            
            # Clean up
            os.unlink(temp_mp3_path)
            
            print(f"{Fore.GREEN}Created speech WAV file: {output_path}{Style.RESET_ALL}")
            return output_path
            
        except ImportError:
            print(f"{Fore.YELLOW}Speech synthesis packages not available.{Style.RESET_ALL}")
            print("Install with: pip install gtts librosa soundfile")
            # Fall back to sine wave
    
    # Create sine wave as fallback
    try:
        import numpy as np
        import soundfile as sf
        
        # Create a sine wave
        duration = 3.0
        sample_rate = 16000
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        audio = 0.5 * np.sin(2 * np.pi * 440 * t)
        
        # Save as WAV
        output_path = os.path.join(input_dir, "dummy_sine.wav")
        sf.write(output_path, audio, sample_rate)
        
        print(f"{Fore.GREEN}Created sine wave WAV file: {output_path}{Style.RESET_ALL}")
        return output_path
        
    except ImportError:
        print(f"{Fore.RED}Could not create dummy file. Install numpy and soundfile.{Style.RESET_ALL}")
        sys.exit(1)


def main() -> Union[Tuple[str, str], List[str], None]:
    """Execute the main transcription workflow based on command line arguments.

    Returns:
        Union[Tuple[str, str], List[str], None]: 
            - For recording: Paths to the audio file and transcript file
            - For file transcription: List of transcription texts
            - None if creating dummy files only

    Raises:
        SystemExit: If an error occurs during execution
    """
    try:
        args = parse_arguments()
        
        # Create dummy file if requested
        if args.create_dummy:
            dummy_path = create_dummy_file(args.dummy_text)
            if not args.file and not args.dir:
                # If only creating dummy file, exit after creation
                return None
            # Otherwise, set the file to transcribe to the dummy file
            args.file = dummy_path
        
        # Determine mode and execute appropriate workflow
        if args.file:
            # File transcription mode
            file_service = FileTranscriptionService()
            return [file_service.transcribe_file(args.file, args.model, args.language)]
            
        elif args.dir:
            # Directory transcription mode
            file_service = FileTranscriptionService()
            return file_service.transcribe_directory(args.dir, args.model, args.language)
            
        else:
            # Default: recording mode
            app_service = ApplicationService()
            return app_service.run(duration=args.duration)
            
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Process interrupted by user.{Style.RESET_ALL}")
        sys.exit(0)
    except (AudioServiceError, FileOperationError) as e:
        print(f"\n{Fore.RED}Error: {e}{Style.RESET_ALL}")
        logger.error(f"Application error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Fore.RED}Unexpected error: {e}{Style.RESET_ALL}")
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
