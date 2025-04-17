# Objective
You will orchestrate the execution of all test prompts in the `test/` folder, analyze the outputs, and generate a summary table that includes the test name, status, and paths to both the test prompt and result files.

# Instructions
1. Scan the `test/` folder for all `.md` files (which are test prompts).
2. For each `.md` test prompt:
   - Execute the test as instructed by the prompt (this may include reading configurations, Dockerfiles, or other input files).
   - Capture the output (Pass/Fail status) and write the result to a file in the `prompt-results/` folder.
   - The result file should be named: `[test_name]-results.md`.
3. After completing all tests, generate a summary table in markdown format with the following columns:
   - **Test Name**: The name of the test (derived from the test file).
   - **Status**: Whether the test passed or failed.
   - **Prompt Path**: The relative path to the `.md` test prompt file.
   - **Result Path**: The relative path to the generated result file.

The summary table should be formatted as:

| Test Name        | Status | Prompt Path            | Result Path                      |
|------------------|--------|------------------------|----------------------------------|
| dockerfile-check | PASS   | test/dockerfile-check.md | prompt-results/dockerfile-check-results.md |
| ...              | ...    | ...                    | ...                              |

### Notes:
- If a test fails, describe why and recommend a fix in the result file.
- Make sure all result files are saved in the `prompt-results/` folder.

