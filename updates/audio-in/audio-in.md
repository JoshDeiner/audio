Here's an updated `README.md` section you can append or integrate into your existing repo. This documents the new **`audio-in` pipeline mode**, the services it uses, and how to run it from the CLI.

---

```markdown
## ? Audio-In Pipeline Mode

The `audio-in` mode enables microphone input ? speech-to-text (STT) transcription using a modular, pluggable pipeline structure. This is useful for real-time voice capture and processing, such as note-taking, speech recognition, or voice-driven interfaces.

---

### ? CLI Usage

```bash
python main.py --pipeline audio-in
```

Optional arguments (already supported):
- `--duration`: Recording duration in seconds (default: 5)
- `--model`: Whisper model size (e.g., tiny, base, small)
- `--language`: Language code to skip detection (e.g., "en")

---

### ? Pipeline Flow

The `audio-in` mode runs the following pipeline:

1. **Capture Audio**
   - Service: `AudioCaptureService`
   - Captures microphone input and returns a WAV buffer or path.

2. **Transcribe Audio**
   - Service: `SpeechToTextService`
   - Uses Whisper to convert audio to text.

3. **Output Result**
   - Outputs transcribed text to the console (or downstream systems in the future).

Optional:
- **Staging (Debug)**
  - Saves audio/text files to a temporary directory for debugging or post-analysis.

---

### ? Services Involved

| Service Name          | Role                               | Location (est.)             |
|-----------------------|------------------------------------|-----------------------------|
| `AudioCaptureService` | Captures mic audio                 | `services/audio_capture.py` |
| `SpeechToTextService` | Converts audio to text             | `services/speech_to_text.py`|
| `StagingService`      | (Optional) Stores files temporarily| `services/staging.py`       |

---


```
