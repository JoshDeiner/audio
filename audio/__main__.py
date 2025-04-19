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
import importlib.util
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
        "--record",
        "-r",
        action="store_true",
        help="Record audio from microphone (default mode)",
    )
    mode_group.add_argument(
        "--file", "-f", metavar="FILE", help="Transcribe a specific audio file"
    )
    mode_group.add_argument(
        "--dir", "-d", metavar="DIR", help="Transcribe all WAV files in a directory"
    )

    # Recording options
    parser.add_argument(
        "--duration",
        "-t",
        type=int,
        default=5,
        help="Recording duration in seconds (default: 5)",
    )

    # Model options
    # Line too long (89 > 88 characters)
    parser.add_argument(
        "--model",
        "-m",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model size (default: from .env or 'tiny')",
    )

    # Language option
    # Line too long (99 > 88 characters)
    parser.add_argument(
        "--language",
        "-l",
        help="Language code to use (e.g., 'en' for English). Skips language detection.",
    )

    # Create dummy file options
    # Line too long (89 > 88 characters)
    parser.add_argument(
        "--create-dummy",
        "-c",
        action="store_true",
        help="Create a dummy WAV file for testing",
    )
    # Line too long (90 > 88 characters)
    parser.add_argument(
        "--dummy-text",
        metavar="TEXT",
        help="Text to use for speech synthesis (requires gtts and librosa)",
    )
    # Seed functionality options
    seed_group = parser.add_argument_group("Seed functionality")
    seed_group.add_argument(
        "--seed",
        action="store_true",
        help="Use seed functionality to generate test audio files",
    )
    # Line too long (96 > 88 characters)
    seed_group.add_argument(
        "--seed-type",
        choices=["sine", "speech", "multi-language", "test-suite"],
        default="sine",
        help="Type of seed audio to generate (default: sine)",
    )
    # Line too long (118 > 88 characters)
    seed_group.add_argument(
        "--output",
        "-o",
        metavar="PATH",
        help="Output path for generated audio file",
    )
    seed_group.add_argument(
        "--frequency",
        type=float,
        default=440.0,
        help="Frequency in Hz for sine wave (default: 440.0)",
    )
    # Line too long (93 > 88 characters)
    seed_group.add_argument(
        "--sample-rate",
        type=int,
        default=16000,
        help="Sample rate in Hz (default: 16000)",
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
            import tempfile

            import librosa
            import soundfile as sf
            from gtts import gTTS

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

            print(
                f"{Fore.GREEN}Created speech WAV file: {output_path}{Style.RESET_ALL}"
            )
            return output_path

        except ImportError:
            print(
                f"{Fore.YELLOW}Speech synthesis packages not available.{Style.RESET_ALL}"
            )
            print("Install with: pip install gtts librosa soundfile")
            # Fall back to sine wave

    # Create sine wave as fallback
    # Line too long (103 > 88 characters)
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

    # Line too long (91 > 88 characters)
    except ImportError:
        print(
            f"{Fore.RED}Could not create dummy file. Install numpy and soundfile.{Style.RESET_ALL}"
        )
        sys.exit(1)


def run_seed_functionality(args: argparse.Namespace) -> Optional[str]:
    """Run seed functionality to generate test audio files.

    Args:
        args: Command line arguments

    Returns:
        Optional[str]: Path to the generated audio file, or None if no file was generated
    """
    # Check if seed scripts are available
    seed_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "seed")
    if not os.path.exists(seed_dir):
        print(f"{Fore.RED}Error: Seed directory not found at {seed_dir}{Style.RESET_ALL}")
        return None
    # Determine output path
    input_dir = os.environ.get("AUDIO_INPUT_DIR", "input")
    os.makedirs(input_dir, exist_ok=True)
    output_path = args.output
    if not output_path:
        if args.seed_type == "sine":
            output_path = os.path.join(input_dir, "dummy_sine.wav")
        elif args.seed_type == "speech":
            output_path = os.path.join(input_dir, "dummy_speech.wav")
        elif args.seed_type == "multi-language":
            output_path = os.path.join(input_dir, "language_samples")
            os.makedirs(output_path, exist_ok=True)
        elif args.seed_type == "test-suite":
            output_path = os.path.join(input_dir, "test_suite")
            os.makedirs(output_path, exist_ok=True)
    
    # Import and run the appropriate seed script
    try:
        if args.seed_type == "sine":
            # Import create_dummy_wav.py
            spec = importlib.util.spec_from_file_location(
                "create_dummy_wav",
                os.path.join(seed_dir, "create_dummy_wav.py")
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Run the script with arguments
                module.create_sine_wave(
                    output_path=output_path,
                    duration=args.duration,
                    frequency=args.frequency,
                    sample_rate=args.sample_rate
                )
                print(f"{Fore.GREEN}Created sine wave WAV file: {output_path}{Style.RESET_ALL}")
                return output_path
        elif args.seed_type == "speech":
            if not args.dummy_text:
                print(f"{Fore.YELLOW}Warning: No text provided for speech synthesis. Using default.{Style.RESET_ALL}")
                text = "This is a test of the audio transcription system."
            else:
                text = args.dummy_text
            # Import create_speech_wav.py
            spec = importlib.util.spec_from_file_location(
                "create_speech_wav", 
                os.path.join(seed_dir, "create_speech_wav.py")
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Run the script with arguments
                module.create_speech_wav(
                    text=text,
                    output_path=output_path,
                    language=args.language or "en"
                )
                print(f"{Fore.GREEN}Created speech WAV file: {output_path}{Style.RESET_ALL}")
                return output_path
        elif args.seed_type == "multi-language":
            # Import create_multi_language_samples.py
            spec = importlib.util.spec_from_file_location(
                "create_multi_language_samples",
                os.path.join(seed_dir, "create_multi_language_samples.py")
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Run the script with arguments
                module.create_language_samples(
                    output_dir=output_path,
                    specific_language=args.language,
                    custom_text=args.dummy_text
                )
                print(f"{Fore.GREEN}Created multi-language samples in: {output_path}{Style.RESET_ALL}")
                return output_path
        elif args.seed_type == "test-suite":
            # Import create_test_suite.py
            spec = importlib.util.spec_from_file_location(
                "create_test_suite",
                os.path.join(seed_dir, "create_test_suite.py")
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Run the script with arguments
                module.create_test_suite(output_dir=output_path)
                print(f"{Fore.GREEN}Created test suite in: {output_path}{Style.RESET_ALL}")
                return output_path
    
    except ImportError as e:
        print(f"{Fore.RED}Error importing seed module: {e}{Style.RESET_ALL}")
        print("Make sure you have installed the required packages:")
        print("pip install numpy soundfile gtts librosa")
        return None
    except Exception as e:
        print(f"{Fore.RED}Error running seed functionality: {e}{Style.RESET_ALL}")
        return None
    return None


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

        # Handle seed functionality if requested
        if args.seed:
            output_path = run_seed_functionality(args)
            if not args.file and not args.dir and output_path:
                # If only creating seed file and not transcribing, exit after creation
                if os.path.isdir(output_path):
                    return None
                # Otherwise set the file to transcribe
                args.file = output_path
        
        # Create dummy file if requested
        elif args.create_dummy:
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
            return file_service.transcribe_directory(
                args.dir, args.model, args.language
            )

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
