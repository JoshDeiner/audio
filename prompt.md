I’m building a stateless audio service that will be containerized and controlled externally.

Please implement **Phase 1A** from the Audio Service Development Phases.  
Refer to the Task Index items **[#1, #2]: `transcriber.py`**.

---

### 🎯 Task Details:
- Use **PyAudio** to capture microphone input  
- Sample at **16kHz**, **mono channel**
- Save the output as `voice.wav` inside a configurable input folder  
  - Use the environment variable `AUDIO_INPUT_DIR` to determine the location  
- This file will later be sent to Whisper for transcription  
- **Do not include transcription logic yet** — just audio capture

---

### ⚙️ Design Constraints:
- The service should be **stateless**  
  - No global variables  
  - No config files  
  - No persistent storage inside the container  
- Use only **environment variables** and **bind-mounted input/output directories**
- Should be designed for future use inside a Docker container

---

### ✅ Output Format:
- Return a single file: `transcriber.py`
- Design it as a callable module (can be run from CLI or invoked from `audio_service.py`)
- Include minimal `print()` logs (e.g. “Recording started…”, “Saved to /path/to/voice.wav”)
- No external dependencies beyond PyAudio and stdlib
