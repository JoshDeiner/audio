Build an asynchronous state machine with the following structure:

1. Define an enum or equivalent for states: LISTENING, SPEAKING, WAITING (optional), STOPPED.

2. Implement an async main loop:
    - Start in LISTENING state.
    - LISTENING:
        - Await an async function that records audio and returns text.
        - Save the text.
        - Transition to SPEAKING.
    - SPEAKING:
        - Await an async function that synthesizes and plays the saved text.
        - Increment a cycle counter.
        - If cycles == n, transition to STOPPED.
        - Else, transition to LISTENING.
    - WAITING (optional):
        - Await a short async sleep.
        - Transition to LISTENING.
    - STOPPED:
        - Exit the loop cleanly.

3. Await all IO operations properly. Do not block.

4. Stub or mock audio-in and audio-out functions with simple async delays and dummy data.

5. Write clean, modular code that supports future expansion (error handling, partial streaming, manual interruption).
