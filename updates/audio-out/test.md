Test: test_tts_then_stt_matches_original_text

Arrange:
    original_text = "The quick brown fox jumps over the lazy dog"
    
    # Initialize services
    tts_service = TextToSpeechService()
    stt_service = SpeechToTextService()
    
    # Optional: staging path for saving audio
    temp_audio_path = "/tmp/test_audio.wav"

Act:
    # Step 1: Generate audio from text
    audio_data = tts_service.synthesize(original_text)

    # Step 2: Save the audio to file (if needed)
    FileService.save(audio_data, path=temp_audio_path)

    # Step 3: Transcribe audio back to text
    transcribed_text = stt_service.transcribe(file_path=temp_audio_path)

Assert:
    # Check that the transcription contains the original content
    assert transcribed_text is not None
    assert len(transcribed_text) > 10
    assert transcribed_text.lower().strip() contains most of original_text.lower().strip()

Cleanup:
    Delete temp_audio_path if it exists

Considerations:
    - Do not expect a perfect match. STT may misinterpret accents, speed, or prosody.
    - Use fuzzy matching if exact match fails (e.g., token overlap, difflib).
    - Audio synthesis and recognition are dependent on model performance and system setup.
    - Test may be flaky if TTS or STT models are inconsistent or hardware is under load.
    - Consider logging intermediate transcription and audio path for debugging.

