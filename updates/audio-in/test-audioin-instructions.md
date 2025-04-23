Create a unit test for the AudioPipelineController class in a file called test_controller_audio_in.py.

The goal is to test the 'audio-in' mode. Use monkeypatching to mock:

1. AudioCaptureService.capture ? mock it to return dummy audio data (e.g., b"fake_wav_data").
2. SpeechToTextService.transcribe ? mock it to return a fixed transcript string (e.g., "this is a test").

Also:
- Capture standard output (stdout) so we can assert that the transcription is printed to the console.
- Use pytest for the test.
- Name the test function test_audio_in_mode_prints_transcription.
- Assert that the mocked transcription string appears in the output.
- Do not call real audio or transcription services.

Keep the test self-contained and focused on verifying controller logic.
