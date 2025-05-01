Create an integration test for a state machine that simulates a conversation loop between a machine and a user. The test must begin with the machine initiating the first message using the audio_out service. The user?s response should be captured using the audio_in service.

Ensure the state machine correctly transitions between the audio_out and audio_in services, and verify that at least one full loop (machine ? user ? machine) completes successfully.

The test should:

Instantiate the state machine.

Start with a machine-generated message via audio_out.

Simulate the user's response captured by audio_in.

Confirm the state machine re-enters the audio_out state with the user input.

Use mocks or test doubles if necessary for the audio services. Output the code for the test.
