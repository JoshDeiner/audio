# Git Hooks Configuration

This project uses Git hooks to maintain code quality:

## Pre-commit Hook

The pre-commit hook automatically applies formatting and linting tools to your code without blocking commits:

- **trailing-whitespace**: Removes trailing whitespace
- **end-of-file-fixer**: Ensures files end with a newline
- **check-yaml**: Validates YAML files
- **check-added-large-files**: Prevents large files from being committed
- **isort**: Sorts Python imports
- **black**: Formats Python code
- **flake8**: Lints Python code (with `--exit-zero` to never block commits)

The pre-commit hook is configured to always allow commits to proceed, even if it makes changes to your files. This allows you to commit freely without being blocked by formatting issues.

## Pre-push Hook

The pre-push hook runs strict checks before allowing code to be pushed to the remote repository:

- **strict-flake8**: Runs flake8 in strict mode
- **strict-mypy**: Runs mypy type checking
- **strict-black**: Ensures code is properly formatted with black
- **strict-isort**: Ensures imports are properly sorted

If any of these checks fail, the push will be blocked until the issues are fixed.

## Implementation Details

The hooks are implemented using:

1. A custom pre-commit script that:
   - Activates the virtual environment
   - Runs pre-commit tools
   - Always exits with success to allow commits

2. A custom pre-push script that:
   - Activates the virtual environment
   - Runs pre-commit with the push stage
   - Blocks pushes if any checks fail

This setup provides a smooth workflow where:
- You can commit freely without interruption
- Your code is automatically formatted during commits
- Strict quality checks are enforced before pushing to the repository
