from services.text_to_speech_service import TextToSpeechService
from services.file_service import FileService
from services.audio_playback_service import AudioPlaybackService
from services.transcription_service import TranscriptionService

class AudioPipelineController:
    def __init__(self, config):
        self.config = config

    def handle_audio_in(self):
        # Step 1: Record audio (assuming handled elsewhere and passed in or mocked for test)
        audio_path = self.config.get("audio_path")

        # Step 2: Transcribe audio
        transcription = TranscriptionService.transcribe(audio_path)
        print("Transcription:", transcription)

        # Step 3: Optionally save
        if self.config.get("save_transcript", False):
            FileService.save_text(transcription, audio_path + ".txt")

        return transcription

    def handle_audio_out(self):
        # Step 1: Resolve text input
        text = self.config.get("text") or self.get_latest_transcription() or "Hello, world!"

        # Step 2: Generate audio
        audio_data = TextToSpeechService.synthesize(text)

        # Step 3: Save audio file
        output_path = self.config.get("output_path") or FileService.generate_temp_output_path()
        FileService.save(audio_data, output_path)

        # Step 4: Optionally play audio
        if self.config.get("play_audio", True):
            AudioPlaybackService.play(audio_data)

        return output_path

    def get_latest_transcription(self):
        try:
            return FileService.load_latest_transcription()
        except FileNotFoundError:
            return None

