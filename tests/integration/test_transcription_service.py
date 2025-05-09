"""Integration test for the complete audio pipeline with text comparison using simplified DI."""

import difflib
import os
import tempfile
from pathlib import Path

import pytest

from audio.audio_pipeline_controller import AudioPipelineController
from library.bin.dependency_injection.app_services import AppServices
from services.implementations.audio_service_impl import AudioRecordingService
from services.implementations.configuration_manager_impl import (
    ConfigurationManager,
)
from services.implementations.file_service_impl import FileService
from services.implementations.transcription_service_impl import (
    TranscriptionService,
)
from services.text_to_speech_service import TextToSpeechService


@pytest.fixture
def app_services():
    """Create AppServices container for tests with a clean configuration."""
    services = AppServices({})

    # Return the services container
    return services


@pytest.mark.integration
def test_full_audio_pipeline(app_services) -> None:
    """Test complete audio pipeline using simplified DI.

    Tests requirements:
    1. Convert text to speech
    2. Convert speech back to text
    3. Compare output with source text
    """
    # Test text input
    test_text = "This is a test passage for the audio pipeline."

    # Step 1: Convert text to speech
    audio_data, sample_rate = TextToSpeechService.synthesize(test_text)

    # Create a temporary file for the audio
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
        temp_audio_file = temp_file.name

    # Save the audio using the file service from app_services
    app_services.file_service.save(
        audio_data=(audio_data, sample_rate), file_path=temp_audio_file
    )

    # Step 2: Transcribe the audio using the transcription service from app_services
    transcribed_text = app_services.transcription_service.transcribe_audio(
        audio_file_path=temp_audio_file, model_size="tiny"
    )

    # Step 3: Compare the original and transcribed text
    print(f"Original: {test_text}")
    print(f"Transcribed: {transcribed_text}")

    # Calculate similarity
    similarity = difflib.SequenceMatcher(
        None, test_text.lower(), transcribed_text.lower()
    ).ratio()
    print(f"Similarity: {similarity:.2f}")

    # Clean up the temporary file
    os.unlink(temp_audio_file)

    # We consider texts similar if they're at least 50% similar
    assert similarity > 0.5, (
        f"Transcription differs too much from original text.\n"
        f"Original: {test_text}\n"
        f"Transcribed: {transcribed_text}\n"
        f"Similarity: {similarity:.2f}"
    )


@pytest.mark.integration
def test_cli_text_to_speech(
    tmp_path: Path,
    app_services,
) -> None:
    """Test the text-to-speech functionality using simplified DI."""
    # Setup temporary directories
    output_dir = tmp_path / "output"
    os.environ["AUDIO_OUTPUT_DIR"] = str(output_dir)
    app_services.config["AUDIO_OUTPUT_DIR"] = str(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    # Create sample text
    test_text = "Testing audio output functionality."
    text_file = tmp_path / "test_input.txt"
    text_file.write_text(test_text)

    # Create output file path
    audio_output_file = tmp_path / "audio_output.wav"

    # Create controller configuration
    config = {
        "data_source": test_text,
        "output_path": str(audio_output_file),
        "play_audio": False,
    }

    # Create controller using factory method
    controller = AudioPipelineController.from_services(config, app_services)

    # Run the pipeline
    import asyncio

    audio_path = asyncio.run(controller.handle_audio_out())

    # Verify audio file was created
    assert (
        audio_output_file.exists()
    ), f"Audio file not created: {audio_output_file}"
    assert audio_output_file.stat().st_size > 0, "Audio file is empty"


@pytest.mark.integration
def test_direct_transcription_service(tmp_path: Path, app_services) -> None:
    """Test direct use of the transcription service with test audio file using simplified DI."""
    # Create a test audio file using TextToSpeechService
    test_text = "This is a test for direct transcription service."
    audio_data, sample_rate = TextToSpeechService.synthesize(test_text)

    # Save to a temporary file using file service from app_services
    test_audio_file = tmp_path / "transcription_test.wav"
    app_services.file_service.save(
        audio_data=(audio_data, sample_rate), file_path=str(test_audio_file)
    )

    # Use the transcription service directly from app_services
    try:
        transcribed_text = app_services.transcription_service.transcribe_audio(
            audio_file_path=str(test_audio_file), model_size="tiny"
        )

        print(f"Transcribed text: {transcribed_text}")

        # Verify we got some transcription
        assert transcribed_text, "No transcription text returned"
        assert len(transcribed_text) > 0, "Empty transcription returned"

        # Calculate similarity
        similarity = difflib.SequenceMatcher(
            None, test_text.lower(), transcribed_text.lower()
        ).ratio()
        print(f"Similarity: {similarity:.2f}")

        # We expect at least some similarity
        assert (
            similarity > 0.3
        ), "Transcription has very low similarity to original text"

    except Exception as e:
        pytest.fail(f"Transcription service failed: {e}")


@pytest.mark.integration
def test_text_file_input_pipeline(
    tmp_path: Path,
    app_services,
) -> None:
    """Test complete audio pipeline using a text file as input via the controller with simplified DI.

    This test verifies that:
    1. The system can read text from a file passed as input
    2. The text can be converted to audio
    3. The audio can be converted back to text
    4. The output text reasonably matches the input text
    """
    # Setup directories
    output_dir = tmp_path / "output"
    os.environ["AUDIO_OUTPUT_DIR"] = str(output_dir)
    app_services.config["AUDIO_OUTPUT_DIR"] = str(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    # Create a text file with a test passage
    test_text = "This is a sample passage that will be read from a text file. It contains multiple sentences to test the audio pipeline functionality."
    input_file = tmp_path / "input_passage.txt"
    input_file.write_text(test_text)

    # Setup audio output file path
    audio_output_file = tmp_path / "text_file_output.wav"

    # Step 1: Convert text from file to speech using the pipeline controller
    config = {
        "data_source": str(input_file),
        "output_path": str(audio_output_file),
        "play_audio": False,
        "return_text_output": False,
    }

    # Create controller using factory method
    controller = AudioPipelineController.from_services(config, app_services)

    # Use asyncio.run to run the coroutine
    import asyncio

    asyncio.run(controller.handle_audio_out())

    # Verify audio file was created
    assert (
        audio_output_file.exists()
    ), f"Audio file not created: {audio_output_file}"
    assert audio_output_file.stat().st_size > 0, "Audio file is empty"

    # Step 2: Transcribe the generated audio file using transcription service from app_services
    transcribed_text = app_services.transcription_service.transcribe_audio(
        audio_file_path=str(audio_output_file), model_size="tiny"
    )

    # Compare original and transcribed text
    print(f"Original text: {test_text}")
    print(f"Transcribed text: {transcribed_text}")

    # Calculate similarity
    similarity = difflib.SequenceMatcher(
        None, test_text.lower(), transcribed_text.lower()
    ).ratio()
    print(f"Similarity: {similarity:.2f}")

    # We consider texts similar if they're at least 50% similar
    assert similarity > 0.5, (
        f"Transcription differs too much from original text.\n"
        f"Original: {test_text}\n"
        f"Transcribed: {transcribed_text}\n"
        f"Similarity: {similarity:.2f}"
    )


@pytest.mark.integration
def test_cli_text_file_input(
    tmp_path: Path,
    app_services,
) -> None:
    """Test complete audio pipeline using a text file as input via API calls with simplified DI.

    This test verifies:
    1. Reading text from a file
    2. Converting to audio
    3. Converting back to text
    4. Comparing input and output text
    """
    # Setup directories
    output_dir = tmp_path / "output"
    os.environ["AUDIO_OUTPUT_DIR"] = str(output_dir)
    app_services.config["AUDIO_OUTPUT_DIR"] = str(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    # Create a text file with a sample passage
    test_text = "This test verifies reading from a text file using the API."
    input_file = tmp_path / "cli_input.txt"
    input_file.write_text(test_text)

    # Setup audio output file path
    audio_output_file = tmp_path / "cli_text_file_output.wav"

    # Create configuration for audio pipeline controller
    config = {
        "data_source": str(input_file),
        "output_path": str(audio_output_file),
        "play_audio": False,
    }

    # Create controller using factory method
    controller = AudioPipelineController.from_services(config, app_services)

    # Run the pipeline
    import asyncio

    audio_path = asyncio.run(controller.handle_audio_out())

    # Verify audio file was created
    assert (
        audio_output_file.exists()
    ), f"Audio file not created: {audio_output_file}"
    assert audio_output_file.stat().st_size > 0, "Audio file is empty"

    # Step 2: Transcribe the generated audio file using the transcription service from app_services
    transcribed_text = app_services.transcription_service.transcribe_audio(
        audio_file_path=str(audio_output_file), model_size="tiny"
    )

    # Compare original and transcribed text
    print(f"Original text: {test_text}")
    print(f"Transcribed text: {transcribed_text}")

    # Calculate similarity
    similarity = difflib.SequenceMatcher(
        None, test_text.lower(), transcribed_text.lower()
    ).ratio()
    print(f"Similarity: {similarity:.2f}")

    # We consider texts similar if they're at least 50% similar
    assert similarity > 0.5, (
        f"Transcription differs too much from original text.\n"
        f"Original: {test_text}\n"
        f"Transcribed: {transcribed_text}\n"
        f"Similarity: {similarity:.2f}"
    )
