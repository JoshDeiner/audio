Create test pseudocode using pytest for a CLI application that uses an AudioPipelineController.

The application supports two main pipeline modes via a --pipeline flag:
- audio-in: Captures audio from the mic, runs speech-to-text (STT), prints the result
- audio-out: Takes text (from --text or a default), runs text-to-speech (TTS), optionally saves and plays audio

The CLI also accepts these optional flags for audio-out:
- --text: Input text to synthesize (optional, can default to "Hello, world!")
- --output: File path to save the audio (optional)
- --play: Flag to play the audio (optional, defaults to True)

Write pytest-style pseudocode for the following test cases:

1. test_audio_in_pipeline_prints_transcription
   - Mock audio capture and STT service
   - Ensure controller prints the expected transcription text

2. test_audio_out_pipeline_uses_default_text
   - Mock TTS service and file saving
   - No --text passed
   - Ensure controller synthesizes default text and saves to a file

3. test_audio_out_pipeline_uses_custom_text_and_output
   - Mock TTS and file writing
   - Provide --text and --output
   - Ensure TTS is called with correct text and audio is saved to the specified path

4. test_audio_out_pipeline_disables_play_when_flag_missing
   - Mock TTS and playback
   - Ensure playback is skipped if --play is False or not passed

Make the tests isolated, mocking external I/O, and use monkeypatch or unittest.mock to simulate service behavior. Each test should include Arrange, Act, and Assert phases in pseudocode form.
