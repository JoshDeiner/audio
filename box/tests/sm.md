Drawing on the information in the sources and our conversation history, here are **imperative instructions for an LLM to turn into pytest code** for testing the asynchronous state machine:

**GOAL:** Generate pytest test functions (`def test_...():`) to validate the behavior of the asynchronous state machine described in the sources, focusing on its states, transitions, cycle handling, and actions.

**ASSUMPTIONS:**
*   You have access to the state machine class (let's assume it's importable).
*   You will use a mocking library like `unittest.mock` (or `pytest_mock` if available) to isolate the state machine logic from external dependencies like audio hardware or APIs. The sources mention "Dependency injection for improved testability", supporting this approach.

**INSTRUCTIONS FOR PYTEST CODE GENERATION:**

1.  **Import Necessary Libraries:** Start the test file by importing `pytest` and a mocking library, for example:
    ```python
    import pytest
    from unittest.mock import MagicMock, patch
    # Assuming the state machine class can be imported like this:
    # from your_module import StateMachine
    ```
    (Replace `your_module` and `StateMachine` with the actual path and class name).

2.  **Mock External Dependencies:** Before defining tests, set up how to mock the external functions or methods the state machine calls for its actions. Mock functions for:
    *   Audio Recording (used in LISTENING state)
    *   Transcription (used in LISTENING state)
    *   Text-to-Speech Synthesis (used in SPEAKING state)
    *   Audio Playback (used in SPEAKING state)
    Use `@patch` decorators on the test functions or use `mocker` fixture if using `pytest_mock`.

3.  **Test Case: Even Cycle Completion (`test_even_cycle_completion`)**
    *   **Define** an asynchronous test function: `async def test_even_cycle_completion(...):` (Use `async` because the state machine is asynchronous).
    *   **Instantiate** the state machine, injecting mock objects for its dependencies.
    *   **Call** the method that runs the state machine, specifically **passing an *even* number of cycles** (e.g., `await state_machine.run(cycles=4, ...)`). The sources show `--cycles N` where N must be even for direct use, or `CYCLES=N`.
    *   **Assert** that after the run method completes, the state machine is in the **`STOPPED` state**. This is the final state when all cycles are complete.
    *   *(Optional, requires introspection or mock assertion):* Assert that the sequence of actions corresponding to LISTENING -> SPEAKING -> WAITING repeated the specified number of times (e.g., mock recording/transcription called 4 times, mock synthesis/playback called 4 times).

4.  **Test Case: Odd Cycle Adjustment (`test_odd_cycle_adjustment`)**
    *   **Define** an asynchronous test function: `async def test_odd_cycle_adjustment(...):`.
    *   **Instantiate** the state machine, injecting mocks.
    *   **Call** the run method, specifically **passing an *odd* number of cycles** (e.g., `await state_machine.run(cycles=3, ...)`). The sources state that odd numbers are automatically increased to the next even number.
    *   **Assert** that after the run method completes, the state machine is in the **`STOPPED` state**.
    *   **Crucially, assert** that the **actual number of cycles executed was the next even number** (e.g., 4 cycles ran, not 3). This might require the state machine or mocks to provide feedback on the number of completed cycles.
    *   *(Optional, requires introspection or mock assertion):* Assert that the sequence of actions corresponding to LISTENING -> SPEAKING -> WAITING repeated the *adjusted* number of times (e.g., 4 times for input 3).

5.  **Test Case: Default Cycles (`test_default_cycles`)**
    *   **Define** an asynchronous test function: `async def test_default_cycles(...):`.
    *   **Instantiate** the state machine, injecting mocks.
    *   **Call** the run method **without explicitly specifying cycles** (e.g., `await state_machine.run(...)`). The sources indicate default parameters are used when cycles are not specified, resulting in 2 cycles.
    *   **Assert** that after the run method completes, the state machine is in the **`STOPPED` state**.
    *   **Assert** that the actual number of cycles executed was **2**, based on the description of default behavior.

6.  **Test Case: State Action Attempts (`test_state_action_attempts`)**
    *   **Define** an asynchronous test function: `async def test_state_action_attempts(...):`.
    *   **Instantiate** the state machine, injecting mocks for recording, transcription, synthesis, and playback.
    *   **Run** the state machine for a small number of cycles (e.g., `await state_machine.run(cycles=2, ...)`).
    *   **Assert** that the mocked functions/methods corresponding to **recording and transcription were called** at least once (representing the LISTENING state actions). Use methods like `mock_record.assert_called()` and `mock_transcribe.assert_called()`.
    *   **Assert** that the mocked functions/methods corresponding to **synthesis and playback were called** at least once (representing the SPEAKING state actions). Use methods like `mock_synthesize.assert_called()` and `mock_play.assert_called()`.

7.  **Test Case: Parameter Passing (`test_parameter_passing`)**
    *   **Define** an asynchronous test function: `async def test_parameter_passing(...):`.
    *   **Instantiate** the state machine, injecting mocks for the functions that consume parameters like duration, model, and language.
    *   **Run** the state machine, passing specific values for `--duration`, `--model`, and `--language` (e.g., `await state_machine.run(cycles=2, duration=10, model="small", language="en", ...)`). The sources mention these parameters.
    *   **Assert** that the mocked recording function was called with the specified `duration`.
    *   **Assert** that the mocked transcription function was called with the specified `model` and `language`.
    *   *(Note: The sources don't explicitly link duration, model, or language to the SPEAKING state, so focus assertions on the LISTENING state actions unless documentation in the `documentation` directory or code suggests otherwise).*

By following these instructions, the LLM should generate pytest code that specifically tests the described behaviors of the `JoshDeiner/audio` asynchronous state machine. Remember that testing asynchronous code in pytest often requires the `pytest-asyncio` plugin and marking async test functions with `@pytest.mark.asyncio`.
