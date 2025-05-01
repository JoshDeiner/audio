# Async State Machine Testing Guide

This document describes the tests implemented for the `AsyncAudioStateMachine` class, which handles the asynchronous audio input/output cycles.

## Cycle Definition

In the AsyncAudioStateMachine:
- One full cycle consists of one LISTENING phase followed by one SPEAKING phase
- The state machine enforces even cycle numbers for balanced operation
- If an odd number is provided, it will be rounded up to the next even number
- A typical sequence for 2 cycles would be: LISTENING → SPEAKING → WAITING → LISTENING → SPEAKING → STOPPED

## Test Structure

Tests for the async state machine are organized into:

1. **Unit Tests** - Testing individual components and state transitions
2. **Integration Tests** - Testing the complete state machine cycle

## Running the Tests

To run all tests:

```bash
pytest
```

To run only the async state machine tests:

```bash
pytest tests/unit/test_async_state_machine.py tests/integration/test_async_state_machine_integration.py tests/integration/test_conversation_state_machine.py
```

To run only unit tests:

```bash
pytest tests/unit/test_async_state_machine.py
```

To run only integration tests:

```bash
pytest tests/integration/test_async_state_machine_integration.py tests/integration/test_conversation_state_machine.py
```

To run only conversation state machine tests:

```bash
pytest tests/integration/test_conversation_state_machine.py
```

## Unit Tests Overview

Unit tests focus on individual state functionality and transitions:

1. **Initial State Test** - Verifies the state machine starts in LISTENING state
2. **Listening State Test** - Tests recording, transcription, and transition to SPEAKING
3. **Speaking State Test** - Tests audio synthesis, playback, and state transitions
4. **Cycles Completion** - Tests that state machine stops after target cycles
5. **Waiting State** - Tests transition from WAITING to LISTENING
6. **Error Handling** - Tests error recovery in LISTENING and SPEAKING states
7. **Complete Run** - Tests the full state machine execution with mocked handlers

## Integration Tests Overview

Integration tests focus on end-to-end functionality and interaction between components:

1. **Full Two-Cycle Run** - Tests a complete two-cycle execution of the state machine
2. **State Transition Sequence** - Verifies states are visited in the correct order
3. **Async Timing Behavior** - Tests proper async behavior and delays
4. **Error Handling in Cycles** - Tests recovery from errors in second audio input
5. **Machine-Initiated Conversation** - Tests conversation flow starting with the machine speaking first
6. **Error Handling in Conversation** - Tests recovery from errors in machine-initiated conversation

## Test Coverage

These tests verify:

- Correct state transitions
- Error recovery and graceful failure
- Asynchronous execution
- Completion of cycles
- Interaction with dependent services

## Implementation Notes

The tests use pytest fixtures to set up:

- Mock services (audio, transcription, config)
- Test environment (directories and environment variables)
- Test configurations

Most tests use `unittest.mock` to patch external functions and services to avoid:
- Recording actual audio
- Playing audio through speakers
- Requiring actual input devices

## Adding New Tests

When adding new tests, follow these patterns:

1. Use `@pytest.mark.unit` or `@pytest.mark.integration` markers
2. For async tests, use `@pytest.mark.asyncio`
3. Use fixtures for setup/teardown
4. Mock external dependencies
5. Verify state transitions and service calls
