#!/usr/bin/env python3
"""
Create Multi-Language Speech Samples.

This script generates WAV files with synthesized speech in multiple languages
to test the audio transcription system's language detection capabilities.
"""

import argparse
import os
import tempfile
from pathlib import Path

import librosa
import soundfile as sf
from gtts import gTTS

# Dictionary of sample texts in different languages
LANGUAGE_SAMPLES = {
    "en": "This is a test of the audio transcription system in English.",
    "fr": "Ceci est un test du système de transcription audio en français.",
    "es": "Esta es una prueba del sistema de transcripción de audio en español.",
    "de": "Dies ist ein Test des Audio-Transkriptionssystems auf Deutsch.",
    "it": "Questo è un test del sistema di trascrizione audio in italiano.",
    "pt": "Este é um teste do sistema de transcrição de áudio em português.",
    "ja": "これは日本語での音声転写システムのテストです。",
    "zh": "这是中文音频转录系统的测试。",
    "ru": "Это тест системы транскрипции аудио на русском языке.",
    "ar": "هذا اختبار لنظام النسخ الصوتي باللغة العربية.",
}


def create_speech_sample(text, output_path, lang):
    """
    Create a WAV file with synthesized speech.

    Args:
        text: Text to convert to speech
        output_path: Path to save the WAV file
        lang: Language code for speech synthesis
    """
    # Create a temporary MP3 file using gTTS
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_mp3:
        temp_mp3_path = temp_mp3.name

    try:
        # Generate speech using gTTS
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(temp_mp3_path)

        # Load the audio file
        audio_data, sample_rate = librosa.load(temp_mp3_path, sr=16000)

        # Save as WAV
        sf.write(output_path, audio_data, sample_rate)
        print(f"Created {lang} speech sample: {output_path}")

    except Exception as e:
        print(f"Error creating {lang} sample: {e}")
    finally:
        # Clean up the temporary MP3 file
        if os.path.exists(temp_mp3_path):
            os.unlink(temp_mp3_path)


def create_all_language_samples(output_dir):
    """
    Create speech samples for all supported languages.

    Args:
        output_dir: Directory to save the WAV files
    """
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    for lang_code, text in LANGUAGE_SAMPLES.items():
        output_path = os.path.join(output_dir, f"sample_{lang_code}.wav")
        create_speech_sample(text, output_path, lang_code)


def main():
    """Parse command line arguments and create language samples."""
    parser = argparse.ArgumentParser(description="Create multi-language speech samples")
    parser.add_argument(
        "--output-dir",
        "-o",
        default="input/language_samples",
        help="Output directory for language samples",
    )
    parser.add_argument(
        "--language",
        "-l",
        help="Specific language code to generate (default: all languages)",
    )
    parser.add_argument(
        "--text", "-t", help="Custom text to use (only with --language)"
    )

    args = parser.parse_args()

    # Ensure the output directory exists
    output_dir = Path(args.output_dir)
    os.makedirs(output_dir, exist_ok=True)

    if args.language:
        # Generate a specific language sample
        if args.language not in LANGUAGE_SAMPLES and not args.text:
            print(
                f"Error: Language '{args.language}' not supported "
                f"and no custom text provided."
            )
            print(f"Supported languages: {', '.join(LANGUAGE_SAMPLES.keys())}")
            return

        text = args.text if args.text else LANGUAGE_SAMPLES.get(args.language)
        output_path = os.path.join(output_dir, f"sample_{args.language}.wav")
        create_speech_sample(text, output_path, args.language)
    else:
        # Generate all language samples
        create_all_language_samples(output_dir)

    print(f"Speech samples saved to: {output_dir}")


if __name__ == "__main__":
    main()
