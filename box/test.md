Got it ? you want a **README** that contains only the **pseudo-code for the tests** (not the system, not the architecture).  
Here?s the correct version focused *only* on the **test pseudo-code**:

---

# ? README: Test Pseudocode for Async Audio-In/Out State Machine

---

## ? Unit Test Pseudocode

---

### 1. Test: System Starts in LISTENING

```plaintext
Setup:
    - Instantiate the state machine.

Assert:
    - Current state == LISTENING.
```

---

### 2. Test: Full Audio-In Completion

```plaintext
Setup:
    - Mock audio_in() to return "Hello, world."

Action:
    - Run LISTENING state logic.

Assert:
    - Captured text == "Hello, world."
    - Transitioned to SPEAKING state.
```

---

### 3. Test: Full Audio-Out Completion

```plaintext
Setup:
    - Mock audio_out("Hello, world.") to complete successfully.

Action:
    - Run SPEAKING state logic.

Assert:
    - audio_out() called with correct text.
    - Correct state transition occurs (LISTENING or STOPPED).
```

---

### 4. Test: One Full Cycle Execution

```plaintext
Setup:
    - Mock audio_in() and audio_out() functions.
    - Set cycles_needed = 2.

Action:
    - Run one listen + speak cycle.

Assert:
    - cycles_completed == 1.
    - State == LISTENING (if more cycles needed).
```

---

### 5. Test: System Stops After N Cycles

```plaintext
Setup:
    - Set cycles_needed = 2.
    - Mock audio_in() and audio_out().

Action:
    - Run full main loop.

Assert:
    - cycles_completed == 2.
    - Final state == STOPPED.
```

---

### 6. Test: Audio-In Error Handling

```plaintext
Setup:
    - Mock audio_in() to raise an exception.

Action:
    - Start in LISTENING state.

Assert:
    - System transitions to STOPPED (or ERROR if implemented).
    - No infinite loop or crash.
```

---

### 7. Test: Audio-Out Error Handling

```plaintext
Setup:
    - Mock audio_out() to raise an exception.

Action:
    - Start in SPEAKING state.

Assert:
    - System transitions to STOPPED (or ERROR if implemented).
    - Proper cleanup behavior.
```

---

## ? Integration Test Pseudocode (n = 2)

---

### 1. Test: Full Two-Cycle Run

```plaintext
Setup:
    - Set n = 2.
    - Mock audio_in() to return ["First message", "Second message"].
    - Mock audio_out() to accept any text.

Action:
    - Run full main loop.

Assert:
    - audio_in() called 2 times.
    - audio_out() called 2 times.
    - Final state == STOPPED.
    - cycles_completed == 2.
```

---

### 2. Test: Correct State Transition Sequence

```plaintext
Setup:
    - Same as above (n = 2).
    - Log the sequence of states during execution.

Action:
    - Run full main loop.

Assert:
    - States visited in this order:
        ["LISTENING", "SPEAKING", "LISTENING", "SPEAKING", "STOPPED"].
```

---

### 3. Test: Async Timing and Await Behavior

```plaintext
Setup:
    - Mock audio_in() and audio_out() to each await asyncio.sleep(0.1).

Action:
    - Run full main loop.

Assert:
    - Total run time ? async timings (not blocked).
    - All mock functions properly awaited.
```

---

### 4. Test: Failure on Second Audio-In

```plaintext
Setup:
    - Mock audio_in() to:
        - First call: return "First message".
        - Second call: raise an exception.
    - Mock audio_out() normally.

Action:
    - Run full main loop.

Assert:
    - audio_in() called twice (second time fails).
    - audio_out() called once.
    - System transitions to STOPPED after failure.
```

---

# ? Test Coverage Summary

| Test Type | Goal |
|:----------|:-----|
| Integration tests | Validate full-cycle behavior and system resilience over multiple loops. |

