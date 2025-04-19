#!/usr/bin/env python3
"""
Create Test Suite for Audio Transcription

This script generates a comprehensive test suite of audio files for testing
the audio transcription system, including various types of audio samples.
"""

import os
import argparse
import numpy as np
import soundfile as sf
from pathlib import Path
import tempfile
from gtts import gTTS
import librosa

def create_sine_wave(duration=3.0, freq=440.0, sample_rate=16000):
    """Create a sine wave audio signal."""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    audio = 0.5 * np.sin(2 * np.pi * freq * t)
    return audio

def create_speech_sample(text, lang="en"):
    """Create a speech sample from text."""
    # Create a temporary MP3 file using gTTS
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_mp3:
        temp_mp3_path = temp_mp3.name
    
    try:
        # Generate speech using gTTS
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(temp_mp3_path)
        
        # Load the audio file
        audio_data, sample_rate = librosa.load(temp_mp3_path, sr=16000)
        return audio_data, sample_rate
        
    finally:
        # Clean up the temporary MP3 file
        if os.path.exists(temp_mp3_path):
            os.unlink(temp_mp3_path)

def create_test_suite(output_dir):
    """Create a comprehensive test suite of audio files."""
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Create sine wave samples at different frequencies
    frequencies = [261.63, 440.0, 880.0]  # C4, A4, A5
    for freq in frequencies:
        output_path = os.path.join(output_dir, f"sine_{int(freq)}hz.wav")
        audio = create_sine_wave(duration=3.0, freq=freq)
        sf.write(output_path, audio, 16000)
        print(f"Created sine wave sample at {freq}Hz: {output_path}")
    
    # 2. Create speech samples with different content lengths
    speech_samples = {
        "short": "This is a short test.",
        "medium": "This is a medium length test of the audio transcription system.",
        "long": "This is a longer test of the audio transcription system. It contains multiple sentences with various words and phrases. The purpose is to test how well the system handles longer audio samples with more complex content."
    }
    
    for name, text in speech_samples.items():
        output_path = os.path.join(output_dir, f"speech_{name}.wav")
        audio_data, sample_rate = create_speech_sample(text)
        sf.write(output_path, audio_data, sample_rate)
        print(f"Created {name} speech sample: {output_path}")
    
    # 3. Create speech samples with numbers and special terms
    special_samples = {
        "numbers": "The test includes numbers like 1, 2, 3, 42, and 100.",
        "dates": "Today is April 19, 2025. The meeting is scheduled for May 5th at 3:30 PM.",
        "technical": "AWS Lambda functions can be triggered by events from Amazon S3, DynamoDB, or API Gateway."
    }
    
    for name, text in special_samples.items():
        output_path = os.path.join(output_dir, f"special_{name}.wav")
        audio_data, sample_rate = create_speech_sample(text)
        sf.write(output_path, audio_data, sample_rate)
        print(f"Created special {name} sample: {output_path}")
    
    # 4. Create multi-language samples
    languages = {
        "en": "This is a test in English.",
        "fr": "Ceci est un test en français.",
        "es": "Esta es una prueba en español.",
        "de": "Dies ist ein Test auf Deutsch."
    }
    
    for lang_code, text in languages.items():
        output_path = os.path.join(output_dir, f"lang_{lang_code}.wav")
        try:
            audio_data, sample_rate = create_speech_sample(text, lang_code)
            sf.write(output_path, audio_data, sample_rate)
            print(f"Created {lang_code} language sample: {output_path}")
        except Exception as e:
            print(f"Error creating {lang_code} sample: {e}")
    
    print(f"\nTest suite created successfully in {output_dir}")
    print(f"Total samples created: {len(frequencies) + len(speech_samples) + len(special_samples) + len(languages)}")

def main():
    parser = argparse.ArgumentParser(description="Create a test suite for audio transcription")
    parser.add_argument("--output-dir", "-o", default="input/test_suite", 
                        help="Output directory for test samples")
    
    args = parser.parse_args()
    create_test_suite(args.output_dir)

if __name__ == "__main__":
    main()
