## Usage

### Using Seed Functionality

The tool includes integrated seed functionality to generate test audio files:

```bash
# Create a sine wave audio file
python -m audio --seed --seed-type sine --frequency 440.0 --duration 5.0

# Create a speech audio file
python -m audio --seed --seed-type speech --dummy-text "This is a test"

# Create multi-language samples
python -m audio --seed --seed-type multi-language

# Create a comprehensive test suite
python -m audio --seed --seed-type test-suite
```

You can also use the Make commands for seed functionality:

```bash
# Create a sine wave audio file
make test-seed-sine

# Create a speech audio file
make test-seed-speech

# Create multi-language samples
make test-seed-multi

# Create a comprehensive test suite
make test-seed-suite
```
