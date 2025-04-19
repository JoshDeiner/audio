#!/usr/bin/env python3
"""
Create Speech WAV Files for Testing

This script generates WAV files with synthesized speech using gTTS (Google Text-to-Speech)
to test the audio transcription system without needing a microphone.
"""

import os
import argparse
import tempfile
from pathlib import Path
from gtts import gTTS
import soundfile as sf
import librosa
import numpy as np

def create_speech_wav(text, output_path, lang="en"):
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
    
    # Generate speech using gTTS
    tts = gTTS(text=text, lang=lang, slow=False)
    tts.save(temp_mp3_path)
    
    try:
        # Load the audio file
        audio_data, sample_rate = librosa.load(temp_mp3_path, sr=16000)
        
        # Save as WAV
        sf.write(output_path, audio_data, sample_rate)
        print(f"Created speech WAV file: {output_path}")
        
    finally:
        # Clean up the temporary MP3 file
        if os.path.exists(temp_mp3_path):
            os.unlink(temp_mp3_path)

def main():
    parser = argparse.ArgumentParser(description="Create speech WAV files for testing")
    parser.add_argument("--text", "-t", required=True, help="Text to convert to speech")
    parser.add_argument("--output", "-o", default="input/speech.wav", help="Output file path")
    parser.add_argument("--language", "-l", default="en", help="Language code (e.g., 'en', 'fr', 'es')")
    
    args = parser.parse_args()
    
    # Ensure the output directory exists
    output_path = Path(args.output)
    os.makedirs(output_path.parent, exist_ok=True)
    
    create_speech_wav(args.text, args.output, args.language)

if __name__ == "__main__":
    main()
