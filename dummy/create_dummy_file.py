"""Utility for creating dummy audio files for testing purposes."""

import os
import sys
import tempfile
from typing import Optional

try:
    import numpy as np
    import soundfile as sf
except ImportError:
    pass

try:
    import librosa
    from gtts import gTTS
except ImportError:
    pass

from colorama import Style 
from colorama import Fore 


def create_dummy_file(text: Optional[str] = None) -> str:
    """Create a dummy WAV file for testing.

    Args:
        text: Optional text for speech synthesis

    Returns:
        str: Path to the created file
    """
    input_dir = os.environ.get("AUDIO_INPUT_DIR", "input")
    os.makedirs(input_dir, exist_ok=True)

    # Early return for text-to-speech path
    if text:
        try:
            # Create a temporary MP3 file using context manager for proper cleanup
            with tempfile.NamedTemporaryFile(
                suffix=".mp3", delete=False
            ) as temp_mp3:
                temp_mp3_path = temp_mp3.name

                # Generate speech
                tts = gTTS(text=text, lang="en", slow=False)
                tts.save(temp_mp3_path)

                # Convert to WAV
                output_path = os.path.join(input_dir, "dummy_speech.wav")
                audio_data, sample_rate = librosa.load(temp_mp3_path, sr=16000)
                sf.write(output_path, audio_data, sample_rate)

            # Clean up temp file after processing
            os.unlink(temp_mp3_path)

            print(
                f"{Fore.GREEN}Created speech WAV file: {output_path}{Style.RESET_ALL}"
            )
            return output_path

        except (ImportError, NameError):
            print(
                f"{Fore.YELLOW}Speech synthesis packages not available.{Style.RESET_ALL}"
            )
            print("Install with: pip install gtts librosa soundfile")
            # Fall back to sine wave

    # Sine wave generation as fallback
    try:
        # Create a sine wave
        duration = 3.0
        sample_rate = 16000
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        audio = 0.5 * np.sin(2 * np.pi * 440 * t)

        # Save as WAV
        output_path = os.path.join(input_dir, "dummy_sine.wav")
        sf.write(output_path, audio, sample_rate)

        print(
            f"{Fore.GREEN}Created sine wave WAV file: {output_path}{Style.RESET_ALL}"
        )
        return output_path

    except (ImportError, NameError):
        print(
            f"{Fore.RED}Could not create dummy file. Install numpy and soundfile.{Style.RESET_ALL}"
        )
        sys.exit(1)
