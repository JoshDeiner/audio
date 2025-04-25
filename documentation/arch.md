# 🧠 Updated Architecture Pattern: Audio-Driven LLM to OS Execution Flow (Modular Monolith)

This architecture follows a **modular monolithic design** — all components run within a single process but are cleanly separated by function for testability and clarity.

This pattern reflects the current prototype focus:
- **Audio-first interaction pipeline** (with optional text input fallback)
- **Stateful controller** with two operational modes:
  - **LLM Mode** (understanding & planning)
  - **OS Mode** (executing validated system actions)
- Wrapper that decides mode transitions and manages system state

---

```
[ User Input (text) ]
        │
        ▼
[ Wrapper Controller ] ◀────────────────────────────┐
        │                                           │
        ▼                                           │
  ┌───────────────────────┐                         │
  │  Scene Context (opt.) │                         │
  │  ──────────────────── │                         │
  │  - Injected at prompt │                         │
  │  - Defines simulated  │                         │
  │    LLM behavior       │                         │
  └───────────────────────┘                         │
        │                                           │
        ▼                                           │
  ┌───────────────┐                                 │
  │   LLM Mode    │                                 │
  │ ───────────── │                                 │
  │ - Send input + scene to LLM                     │
  │ - Receive JSON: response + action candidate     │
  │ - Validate structure + intent clarity           │
  │ - If action is clear + valid ➝ inform wrapper   │
  └───────────────┘                                 │
        │                                           │
        ▼                                           │
┌─────────────────────┐                             │
│   Wrapper Switches   │                            │
│   to OS Mode         │                            │
└─────────────────────┘                             │
        │                                           │
        ▼                                           │
  ┌───────────────┐                                 │
  │   OS Mode     │                                 │
  │ ───────────── │                                 │
  │ - Receive structured action (type + value)      │
  │ - Validate (path exists, action safe, etc.)     │
  │ - Execute using `os.system()` or `subprocess`   │
  │ - Log result + status                           │
  └───────────────┘                                 │
        │                                           │
        ▼                                           │
[ Result or next input → back to Wrapper ] ─────────┘
```

---

## 🔁 Wrapper Responsibilities

| Responsibility        | Description |
|------------------------|-------------|
| **Flow controller**    | Decides active mode (LLM or OS) based on latest LLM output |
| **Context memory**     | Tracks user input, LLM response, and actions |
| **Guardrails**         | Validates intent/action before execution |
| **Transition logic**   | Switches from LLM ➝ OS ➝ LLM as needed |
| **Action refinement**  | If action is vague or missing fields, asks LLM follow-up questions |

---

## ✅ LLM Mode (with Fallback Strategy)
- Accepts raw user input
- Sends prompt + context to LLM (local or cloud)
- Expects structured output:
```json
{
  "response": "Sure, opening your browser now.",
  "action": {
    "type": "launch_app",
    "app_name": "firefox"
  }
}
```
- If no valid action → remains in LLM mode
- If partially valid → requests clarification
- If invalid or unclear for 3 consecutive turns → logs incident and escalates gracefully (e.g. fallback message or scene reset)
- If valid and safe → wrapper switches to OS Mode

---

## 🧯 Handling LLM Uncertainty

When the LLM is unsure, confused, or off-track, the system should catch this early and handle it gracefully. Common signs:
- Missing `action` field
- Ambiguous or nonsensical command
- Off-topic dialogue or repetition

### 🔁 Suggested Strategy
| Attempt | Behavior |
|--------|----------|
| 1st    | Ask for clarification (e.g., "Can you clarify what you want me to do?") |
| 2nd    | Retry with additional scene context or guidance |
| 3rd    | Log confusion, escalate or reset scene with fallback response |

This logic lives in the **wrapper**, and keeps the assistant on-track while allowing for error recovery and logging in user testing.

---

## 🎭 Scene Injection Support (LLM as Simulated User)

This architecture also supports an alternate interaction pattern: simulating the **LLM as the user** in a help desk scene, where the human acts as the support agent.

This adds scene context that influences the LLM’s behavior while keeping the wrapper/controller pattern intact.

### 🎯 Goal:
Enable LLM to play a scripted or dynamic user role within a help desk simulation.

### 🧩 Where it fits:
- Scene definition is injected into LLM prompts during **LLM Mode**
- The wrapper includes optional `scene_context` at the start of interaction or before each prompt

### 🔁 Scene Injection Logic
| Step | Behavior |
|------|----------|
| 1. Scene defined (e.g. JSON or YAML) | `{ "role": "confused user", "issue": "can't open PDF in Google Drive" }` |
| 2. Scene prepended to LLM input | Prompt begins with: _"You are a user calling the help desk..."_ |
| 3. Interaction begins | System responds as help desk agent |
| 4. Mode switch logic still applies | If LLM generates action → wrapper switches to OS Mode |

### ✅ Architecture Integrity
This design preserves the state machine because:
- It does not change how modes transition
- Scene context is part of `LLM input generation`, not controller logic
- Controller still switches only on valid action detection

### 📁 Optional Scene Format (with Constraints)
```json
{
  "scene": "User can't open file",
  "role": "user",
  "persona": "frustrated novice",
  "problem": "Can't open .pdf from Google Drive",
  "tone": "impatient but polite",
  "constraints": [
    "Do not interrupt the agent",
    "Always try the help desk's suggestion once before asking again",
    "Do not use technical language"
  ]
}
```

---

## 🧱 Scene Construction Strategy

### 🎯 Goal:
Enable the definition of flexible yet guided simulation scenarios where the LLM behaves according to structured rules — while still generating dynamic, realistic dialogue.

---

### 🔁 Hybrid Scene Flow Pattern
Use a **hybrid structure** that combines:
- **Structured fields** (scene intent, role, tone, boundaries)
- **LLM-driven responses** that adapt inside those constraints

| Layer                | Controlled By | Role |
|----------------------|---------------|------|
| Scene Metadata       | Human / UI    | Defines scenario constraints (goal, persona, tone) |
| System Prompt Builder | Wrapper       | Combines metadata + input → prompt to LLM |
| LLM Output           | LLM           | Simulates dynamic user behavior or help desk responses |
| Flow Control         | Wrapper       | Ensures logic stays within expected mode transitions |

---

### 📐 Tools to Enable Specific Flow

#### ✅ 1. **Scene Templates (JSON/YAML)**
- Define scenes with:
  - `role`: who the LLM is acting as
  - `persona`: tone and confidence
  - `goal`: the outcome to reach
  - `steps` or `phases`: optional step-by-step structure

#### ✅ 2. **Prompt Chaining with Flow Constraints**
- Include flow markers in the prompt like:
  > "You are on step 1 of 3. Your goal is to describe your problem."

- Update this as the conversation progresses

#### ✅ 3. **Scenario Controller Module** (Optional)
- Tracks which step in the flow the LLM should be simulating
- Injects scene metadata into the LLM input
- Handles transitions, retries, or resets

#### ✅ 4. **Turn Limiting + Branching Logic**
- Cap number of turns per scene
- Use scene metadata to determine expected branches (e.g. clarification vs success)

---

### 🧪 Example Scene (Structured + Flow Metadata)
```json
{
  "scene": "Help user open a PDF",
  "persona": "frustrated but polite beginner",
  "goal": "Get help opening a PDF from Google Drive",
  "steps": [
    { "step": 1, "intent": "User describes the problem" },
    { "step": 2, "intent": "User follows instruction to check Downloads folder" },
    { "step": 3, "intent": "User confirms file opened successfully" }
  ]
}
```

This can be converted to structured prompt input to the LLM like:
```
You are a beginner user calling the help desk.
Step 1 of 3: Describe the problem you're having opening a PDF from Google Drive.
```

---

### ✅ Summary
This strategy lets you:
- Keep LLM behavior **on-rails** but still natural
- Simulate **realistic user conversations**
- Adapt and evolve scenarios with minimal overhead
- Integrate easily with your current wrapper/controller

Let me know if you'd like a starter scene loader or prompt-injection helper function.

---

## 🧩 Audio Service Integration Design

This section defines a **separate audio service** that interacts with the main monolithic LLM–OS controller. This service will handle both **audio input** and **audio output**, acting as a dedicated I/O layer that feeds into and responds from the state machine.

---

### 🎯 Audio Service Goals
- Continuously **capture microphone input**, convert to text using Whisper
- Receive **text responses from the LLM**, convert to audio, and play to the user
- Communicate with the monolithic system via **queue or messaging protocol** (e.g. in-memory Queue, Redis pub/sub)

---

### 🛠 Architecture Overview
```
[ Mic Input (PyAudio) ]
        │
        ▼
[ Whisper Transcription ]
        │
        ▼                [ Main LLM-OS Controller ]
[ Audio Input Queue ] ───────────────▶ [ LLM / Wrapper / OS Modes ]
                                      │
[ Audio Output Queue ] ◀─────────────┘
        │
        ▼
[ TTS (Coqui, pyttsx3, etc.) ]
        │
        ▼
[ PyAudio Speaker Output ]
```

---

### 📦 Service Components

This layer includes a bi-directional audio-text bridge:

| Component              | Description |
|------------------------|-------------|
| `transcriber.py`       | Takes PyAudio audio input and transcribes to text via Whisper |
| `synthesizer.py`       | Converts LLM text output to speech and plays via PyAudio or streaming playback |

---

### 🔄 Transcription + Synthesis Flow

| Direction | Flow |
|-----------|------|
| Mic → LLM | `PyAudio` → `transcriber.py` → `Whisper` → text → `LLM` |
| LLM → User | LLM output (text) → `synthesizer.py` → TTS engine → audio → speaker

Whisper is used in the forward direction (speech → text). For text → speech, use TTS (not Whisper, which does not synthesize audio).

| Module              | Description |
|---------------------|-------------|
| `audio_service.py`  | Entry point: runs audio listener and playback loop |
| `input_stream.py`   | Captures audio from mic using PyAudio, pushes to Whisper, stores in queue |
| `output_stream.py`  | Pulls from output queue, converts text to speech, plays to speaker |
| `audio_queue.py`    | Queue abstraction layer (can support `queue.Queue`, `multiprocessing.Queue`, or Redis) |

---

### 🧰 Technologies

| Function        | Recommended Tools |
|-----------------|-------------------|
| Mic Input       | PyAudio           |
| Transcription   | `whisper.cpp` or `whisper-python` |
| TTS             | `pyttsx3`, `Edge-TTS`, `Coqui TTS` |
| Queuing         | Python `queue`, Redis (for external systems) |
| Playback        | PyAudio, `playsound`, `ffmpeg` |

---

### 🔁 Communication Contract
- **Input Queue**: `audio_service` → `wrapper`
  - Format: `{ "text": "user transcript", "timestamp": ... }`
- **Output Queue**: `wrapper` → `audio_service`
  - Format: `{ "response": "Sure, I can help.", "voice": true }`

---

## ♻️ Stateless Audio Service Design Pattern

This audio service is designed to be **stateless** — it holds no persistent data and operates only on the input it receives at runtime. All input and output are passed via mounted file directories or messaging queues. This makes the service clean, composable, and portable.

---

### ✅ Key Principles
- **No internal storage**: audio/text data comes from external inputs
- **Configurable by environment variables** (no internal configs)
- **Bind-mounted volumes or queues** define data flow
- **Logs to stdout or mounted log directory**
- **Modular processing**: audio in → text out, or text in → audio out

---

### 🗂️ Option 1: File-Based Interaction (Preferred for Prototypes)

**Use Case:** Mount input/output folders to the container, trigger processing, collect results.

| Purpose | Path in Docker | Notes |
|---------|----------------|-------|
| Audio Input | `/data/in/voice.wav` | Recorded or preloaded input |
| Text Input | `/data/in/say.txt` | Optional machine-started TTS trigger |
| Transcript Output | `/data/out/transcript.txt` | Whisper transcription result |
| Audio Response | `/data/out/response.wav` | TTS-generated reply |

**Docker Run Example:**
```bash
docker run \
  -v $(pwd)/input:/data/in \
  -v $(pwd)/output:/data/out \
  -e AUDIO_INPUT_DIR=/data/in \
  -e AUDIO_OUTPUT_DIR=/data/out \
  audio-service:latest
```

This layout works cleanly with Phases 1A–1D and allows other services (like the wrapper) to read/write data to these paths without tight coupling.

---

### 🧩 Notes for Future Expansion
- Redis or ZeroMQ queue versions can be swapped in for dynamic pipelines
- File-based mode remains ideal for debugging, testing, or static demos

---

### 🧱 Audio Service Development Phases

These phases describe the progressive flow of the audio service, broken down into independently testable layers:

#### 🌀 Phase 1: Audio Input Capture
- Goal: Capture live voice input using microphone.
- Tools: `PyAudio`
- Output: Raw audio stream or `.wav` data

#### ⏺️ Phase 1B: Push-to-Talk Control
- Goal: Introduce manual control to start and stop microphone recording.
- Behavior: Wait for a key press (e.g. Enter) to begin recording. Automatically stop after a set duration (e.g. 5 seconds) or a second key press.
- Tools: `PyAudio`, `keyboard` or `input()`
- Benefits:
  - Reduces background noise and false triggers
  - Gives the user control over when to speak
  - Easier for debugging and demonstrations
- Output: Audio file or buffer passed to Whisper transcription pipeline

#### 🧪 Phase 1C: Trigger-Based Round-Trip Response Test
- Goal: Validate full input-output loop using a mock response.
- Behavior:
  - User says "hi josh"
  - Whisper transcribes input
  - If match found (`transcript == 'hi josh'`), play a pre-recorded audio response (e.g. `hi_response.wav`)
- Tools: `PyAudio`, `Whisper`, `playsound` or `PyAudio` playback
- Benefits:
  - Validates mic input → transcription → audio output without full LLM integration
  - Repeatable test for round-trip system behavior
  - Easy to extend by replacing hardcoded response with dynamic LLM + TTS

#### 🗣️ Phase 1D: Simulated Machine-Initiated Greeting
- Goal: Test system output starting with a machine-generated response.
- Behavior:
  - Simulate a system event (e.g. timer, command, or trigger)
  - Read a line of text from a file (e.g., `response.txt`)
  - Convert the text (e.g. "hi everyone") into speech using a TTS engine
  - Play the resulting audio to the user through speakers
- Tools: TTS engine (`pyttsx3`, `Coqui`, etc.), `PyAudio` or `playsound`
- Benefits:
  - Validates TTS-to-audio pipeline from static or scripted inputs
  - Helps simulate assistant “proactive” voice responses
  - Allows repeatable test cases using simple text file editing
- Behavior:
  - Simulate a system event (e.g. timer, command, or trigger)
  - Text response like "hi everyone" is sent through TTS
  - Resulting audio is played to the user through speakers
- Tools: TTS engine (`pyttsx3`, `Coqui`, etc.), `PyAudio` or `playsound`
- Benefits:
  - Validates TTS-to-audio pipeline from static or scripted inputs
  - Helps simulate assistant “proactive” voice responses
  - Establishes a baseline for outbound speech flow using a mock response.
- Behavior:
  - User says "hi josh"
  - Whisper transcribes input
  - If match found (`transcript == 'hi josh'`), play a pre-recorded audio response (e.g. `hi_response.wav`)
- Tools: `PyAudio`, `Whisper`, `playsound` or `PyAudio` playback
- Benefits:
  - Validates mic input → transcription → audio output without full LLM integration
  - Repeatable test for round-trip system behavior
  - Easy to extend by replacing hardcoded response with dynamic LLM + TTS
- Behavior: Wait for a key press (e.g. Enter) to begin recording. Automatically stop after a set duration (e.g. 5 seconds) or a second key press.
- Tools: `PyAudio`, `keyboard` or `input()`
- Benefits:
  - Reduces background noise and false triggers
  - Gives the user control over when to speak
  - Easier for debugging and demonstrations
- Output: Audio file or buffer passed to Whisper transcription pipeline
- Goal: Capture live voice input using microphone.
- Tools: `PyAudio`
- Output: Raw audio stream or `.wav` data

#### 🧠 Phase 2: Speech-to-Text Conversion
- Goal: Convert microphone input into text.
- Tools: `whisper.cpp`, `whisper-python`
- Input: Raw audio or stream
- Output: Clean user transcript (text)

#### 🖥️ Phase 3: Processed Text Output
- Goal: Use the transcribed text for downstream tasks.
- Options:
  - Log to console for debugging
  - Send to the main monolithic wrapper via in-memory queue or Redis
  - Store in file or send to networked service

---

### 🗂️ Task Index for Audio Service

1. `audio_service.py` — Launches and coordinates the audio input and output loops.
2. `transcriber.py` — Captures microphone input via PyAudio, transcribes it using Whisper, and pushes text into a queue.
3. `synthesizer.py` — Reads text responses from a queue, converts them to audio using TTS (e.g. Coqui, pyttsx3), and plays through speaker.
4. `audio_queue.py` — Provides an abstraction layer over in-memory Queue or Redis for audio in/out messaging.
5. `message_format.py` — Defines the data structure for queue messages, including timestamps, speaker ID, and content type (text/audio).

---

### ✅ Integration Plan
1. Launch `audio_service.py` as a standalone service (or thread/subprocess)
2. Main controller polls or subscribes to `audio_input_queue`
3. Controller processes message as if it came from a user
4. When wrapper generates a response, it pushes it to `audio_output_queue`
5. Audio service reads from output queue, converts to audio, plays to user

Would you like a standalone version of this audio service scaffolded in code?

---

## 🔊 Updated Audio Support Pattern

This architecture now supports audio-first interaction using a local microphone and speaker. Audio acts as the primary interface:
- **Audio In** → captured via `PyAudio` (or similar), transcribed by `Whisper`
- **LLM** processes transcribed text and returns a text response
- **Audio Out** → text converted to speech and played back to the user

### 🎯 Flow Summary
1. User speaks into mic
2. `PyAudio` captures audio stream
3. Audio sent to `Whisper` for transcription
4. Text sent to LLM as input (Claude, LLaMA, etc.)
5. LLM generates response (JSON: text + action)
6. Response text sent to TTS (e.g. `pyttsx3`, `Coqui`)
7. Audio played back to user via speaker using `PyAudio`, `playsound`, or `ffmpeg`

---

### 📐 Integrated Audio Flow
```
[ User Mic Input ]
       │
       ▼
[ PyAudio Capture ]
       │
       ▼
[ Whisper Transcription ]
       │
       ▼
[ Wrapper Controller ] ◀────────────────────────────┐
       │                                            │
       ▼                                            │
 ┌───────────────────────┐                          │
 │ Scene Context (opt.)  │                          │
 └───────────────────────┘                          │
       │                                            │
       ▼                                            │
 ┌───────────────┐                                  │
 │   LLM Mode    │                                  │
 └───────────────┘                                  │
       │                                            │
       ▼                                            │
 ┌───────────────┐                                  │
 │   OS Mode     │                                  │
 └───────────────┘                                  │
       │                                            │
       ▼                                            │
[ TTS (e.g., Coqui) ]                              │
       │                                            │
       ▼                                            │
[ PyAudio / Speaker Output ] ──────▶ External Service (opt)
```

---

### 🛠 Recommended Tools for Audio Pipeline
| Role               | Tool Options                                   |
|--------------------|------------------------------------------------|
| Mic Audio Capture  | `PyAudio`, `sounddevice`                       |
| Transcription      | `whisper.cpp`, `whisper-python`               |
| Text-to-Speech     | `pyttsx3`, `Coqui`, `Edge-TTS`, `gTTS`         |
| Speaker Output     | `PyAudio` playback, `playsound`, `ffmpeg`     |
| Background Routing | `streamer.py` (broadcast or log audio out)    |

---
```
├── audio/
│   ├── audio_input.py       # Speech-to-text using Whisper
│   ├── audio_output.py      # Text-to-speech wrapper
│   └── streamer.py          # Optional audio router/broadcaster
```

---

### ✅ Summary
This architecture supports audio with minimal changes:
- **Audio input = text entry replacement**
- **Audio output = response channel**
- Easily pluggable into existing wrapper flow

Would you like a script that connects Whisper live STT with your wrapper?

---

## ✅ OS Mode
- Receives fully structured action object
- Runs validation logic (e.g., `whitelist`, `os.path.exists()`)
- Executes system call (via `subprocess.run()` or `os.system()`)
- Logs results and returns to LLM mode for next turn

---


---

## ✅ Summary Table

| Component       | Purpose |
|----------------|---------|
| `Wrapper`       | Central logic & state controller |
| `LLM Mode`      | Understands user, suggests action |
| `OS Mode`       | Executes real actions on system |
| `Transition`    | Based on action confidence and validation |
| `Refinement`    | Prompts LLM if action is ambiguous or incomplete |

---

This structure sets you up for easy testing, simulation, and future audio or GUI extension.

---

## 🧱 Recommended Code Organization: Modular Monolith

A modular monolith gives you structured separation of logic without the overhead of microservices or distributed complexity.

### 📦 Suggested Project Layout
```
voice-assistant/
│
├── main.py                   # Starts app, routes user input
├── config.py                 # Constants, scene templates, paths
│
├── controller/               # Wrapper state machine
│   └── wrapper.py            # Core class controlling LLM ↔ OS flow
│
├── modes/
│   ├── llm_mode.py           # LLM handling, response parsing, validation
│   ├── os_mode.py            # Action executor (safe commands, logging)
│
├── prompts/
│   ├── scene_loader.py       # Load scene files (JSON/YAML)
│   ├── prompt_builder.py     # Compose LLM prompt from scene + state
│
├── llm/
│   └── local_llm.py          # Interface to Claude, LLaMA, or Gemini
│
├── tools/
│   ├── logger.py             # Action/result logging
│   ├── validator.py          # Safety checks for commands/actions
│   └── file_utils.py         # Helpers like checking file paths
│
├── tests/
│   ├── test_wrapper.py
│   └── test_prompt_generation.py
│
└── scenes/
    └── chrome_help.json      # Example scene files

