import os
import sys
import importlib.util
import argparse
from typing import Optional

from colorama import Fore, Style  # type: ignore


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
        print(
            f"{Fore.RED}Error: Seed directory not found at {seed_dir}{Style.RESET_ALL}"
        )
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
                os.path.join(seed_dir, "create_dummy_wav.py"),
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Run the script with arguments
                module.create_sine_wave(
                    output_path=output_path,
                    duration=args.duration,
                    frequency=args.frequency,
                    sample_rate=args.sample_rate,
                )
                print(
                    f"{Fore.GREEN}Created sine wave WAV file: {output_path}{Style.RESET_ALL}"
                )
                return str(output_path)

        elif args.seed_type == "speech":
            if not args.dummy_text:
                print(
                    f"{Fore.YELLOW}Warning: No text provided for speech synthesis. Using default.{Style.RESET_ALL}"
                )
                text = "This is a test of the audio transcription system."
            else:
                text = args.dummy_text

            # Import create_speech_wav.py
            spec = importlib.util.spec_from_file_location(
                "create_speech_wav",
                os.path.join(seed_dir, "create_speech_wav.py"),
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Run the script with arguments
                module.create_speech_wav(
                    text=text,
                    output_path=output_path,
                    language=args.language or "en",
                )
                print(
                    f"{Fore.GREEN}Created speech WAV file: {output_path}{Style.RESET_ALL}"
                )
                return str(output_path)

        elif args.seed_type == "multi-language":
            # Import create_multi_language_samples.py
            spec = importlib.util.spec_from_file_location(
                "create_multi_language_samples",
                os.path.join(seed_dir, "create_multi_language_samples.py"),
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Run the script with arguments
                module.create_language_samples(
                    output_dir=output_path,
                    specific_language=args.language,
                    custom_text=args.dummy_text,
                )
                print(
                    f"{Fore.GREEN}Created multi-language samples in: {output_path}{Style.RESET_ALL}"
                )
                return str(output_path)

        elif args.seed_type == "test-suite":
            # Import create_test_suite.py
            spec = importlib.util.spec_from_file_location(
                "create_test_suite",
                os.path.join(seed_dir, "create_test_suite.py"),
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Run the script with arguments
                module.create_test_suite(output_dir=output_path)
                print(
                    f"{Fore.GREEN}Created test suite in: {output_path}{Style.RESET_ALL}"
                )
                return str(output_path)

    except ImportError as e:
        print(f"{Fore.RED}Error importing seed module: {e}{Style.RESET_ALL}")
        print("Make sure you have installed the required packages:")
        print("pip install numpy soundfile gtts librosa")
        return None
    except Exception as e:
        print(
            f"{Fore.RED}Error running seed functionality: {e}{Style.RESET_ALL}"
        )
        return None

    return None