Of course ? here?s a **clean imperative prompt** you can give to an LLM:

---

# ? Imperative LLM Prompt

```
Create an asynchronous state machine that loops between audio input (speech-to-text) and audio output (text-to-speech) for a fixed number of cycles.

Requirements:

- Use an enum or similar construct to define four states: LISTENING, SPEAKING, WAITING (optional), and STOPPED.
- Implement a main asynchronous function that:
    - Starts in the LISTENING state.
    - In the LISTENING state:
        - Asynchronously record audio from the microphone.
        - Wait for the recording to finish and produce text output.
        - Store the text result and transition to the SPEAKING state.
    - In the SPEAKING state:
        - Asynchronously synthesize and play the stored text.
        - After speaking completes:
            - Increment a cycle counter.
            - If the number of completed cycles equals the target `n`, transition to STOPPED.
            - Otherwise, transition back to LISTENING.
    - In the WAITING state (optional):
        - Asynchronously pause for a short duration (e.g., 0.1 seconds).
        - Transition to LISTENING afterward.
    - In the STOPPED state:
        - Exit the loop cleanly.
- Ensure that all audio operations (`audio_in`, `audio_out`) are awaited and do not block the event loop.
- Keep the structure simple but allow for easy future expansion (e.g., adding error handling, dynamic state transitions).
- Do not implement the actual audio-in or audio-out functionality. Stub or mock them as needed (e.g., simulated sleep and dummy text).
- Maintain clean separation between states and transitions.
