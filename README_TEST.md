# Testing the Audio Transcription Tool with Dummy Files

This guide explains how to test the audio transcription tool using dummy WAV files instead of recording audio in real-time. This is useful for development and testing when you're away from a microphone or in an environment where recording isn't possible.

## Setup

1. Make sure you have installed all the required dependencies:
   ```bash
   pip install -r requirements.txt
   pip install gtts librosa  # For speech synthesis testing
   ```

2. Ensure your `.env` file is properly configured:
   ```
   AUDIO_INPUT_DIR=input
   AUDIO_OUTPUT_DIR=output
   WHISPER_MODEL=tiny
   WHISPER_COMPUTE_TYPE=float32
   WHISPER_DEVICE=auto
   ```

## Testing Options

### Option 1: Automated Test Script

Run the automated test script that creates dummy files and processes them:

```bash
./test_transcription.sh
```

This script will:
1. Create a sine wave WAV file
2. Create a speech WAV file (if gtts and librosa are installed)
3. Run the transcription on these files
4. Save the results to the output directory

### Option 2: Manual Testing

#### Step 1: Create Dummy WAV Files

Create a simple sine wave WAV file:
```bash
python create_dummy_wav.py --output input/sine_wave.wav --duration 3.0 --frequency 440.0
```

Create a speech WAV file:
```bash
python create_speech_wav.py --text "This is a test of the audio transcription system." --output input/test_speech.wav
```

#### Step 2: Run the Transcription

Process all WAV files in the input directory:
```bash
python file_transcriber.py
```

Or process specific files:
```bash
python file_transcriber.py input/test_speech.wav
```

### Option 3: Use Your Own WAV Files

1. Place your WAV files in the `input` directory
2. Run the transcription:
   ```bash
   python file_transcriber.py
   ```

## Expected Results

After running the transcription, check the `output` directory for text files containing the transcriptions. Each file will be named after the original WAV file with a timestamp.

For speech files, you should see the transcribed text. For sine wave files, the results may vary as they don't contain actual speech.

## Troubleshooting

- **Missing dependencies**: Make sure all required packages are installed
- **File not found errors**: Ensure the input directory exists and contains WAV files
- **Transcription errors**: Try using a different Whisper model by changing the `WHISPER_MODEL` in your `.env` file

## Next Steps

Once you've verified that the transcription works with dummy files, you can:

1. Integrate this functionality into your main application
2. Experiment with different Whisper models for better accuracy
3. Add support for more audio formats
4. Implement batch processing for multiple files
