I need help implementing a specific part of Phase 1C from my audio processing architecture: transcribing audio to text and writing the result to an output file.

I already have a working `transcriber.py` that records audio from a microphone and saves it as a WAV file in an input directory. Now I need to:

1. Add Whisper integration to transcribe the recorded audio file
2. Write the transcription to a text file in the output directory

Requirements:
- Build on my existing `transcriber.py` code
- Add a function to transcribe the WAV file using Whisper (whisper-python)
- Write the transcription to a file named "transcript.txt" in the output directory (from AUDIO_OUTPUT_DIR environment variable)
- Include proper error handling and logging
- Keep the code modular and well-commented

Please provide just the additional code needed to implement this specific functionality.

