# Objective
Analyze the provided project directory and determine whether the application is likely to start and run successfully in a local development environment.

# Assumption
The entry script for local startup is `python transcriber.py`.

# Instructions
1. Check for the presence and validity of the following:
   - Entry point script: `transcriber.py`
   - Dependency manifest (`requirements.txt`, `pyproject.toml`, or similar)
   - Local run/start command (`python transcriber.py`)
   - Environment file (`.env`) or configuration file requirements
   - Port conflicts or hardcoded ports
   - Required files or directories referenced by the script (e.g. static assets, audio files, config files)

2. Simulate a local run-time pass/fail result.
   - For run-time, check for likely issues such as:
     - Missing or malformed `transcriber.py`
     - Missing dependencies
     - Missing environment variables
     - Hardcoded paths or misconfigured imports

3. Output the analysis in the following format (markdown):

## Local Run Startup Report
- Status: [PASS / FAIL]
- Reason(s):
  - [Brief explanation for each issue]
- Startup Warnings (if any):
  - [Warnings such as missing .env, unused imports, hardcoded values, etc.]
- Environment Assumptions:
  - [List of required environment variables or files not found in the local directory]

## Recommendations
- [Suggestions for fixing issues or improving local development startup]

4. Save the final output to a file named `local-run-check-[FOLDERNAME].md` inside a folder called `prompt-results`. If the folder does not exist, create it.

