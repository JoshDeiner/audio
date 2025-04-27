.PHONY: help setup docker-run local-run docker-build docker-stop clean test-dummy test-dummy-speech test-dummy-en test-file test-dir test-file-en test-dir-en test-file-model test-dir-model test-suite test-languages test-seed-sine test-seed-speech test-seed-multi test-seed-suite transcribe transcribe-en transcribe-model test test-unit test-integration audio-in audio-out conversation

# Default Python interpreter and pip
PYTHON := python3
PIP := pip3
VENV := venv

help:
	@echo "Audio Recording App Makefile"
	@echo ""
	@echo "Available commands:"
	@echo "  make setup              - Install dependencies and create virtual environment"
	@echo "  make docker-run         - Run the application in Docker"
	@echo "  make local-run          - Run the application locally"
	@echo "  make docker-build       - Rebuild the Docker image"
	@echo "  make docker-stop        - Stop any running Docker containers"
	@echo "  make clean              - Remove temporary files and virtual environment"
	@echo ""
	@echo "Command-line commands:"
	@echo "  make audio-in           - Run the audio-in pipeline (transcription)"
	@echo "  make audio-out          - Run the audio-out pipeline (text-to-speech)"
	@echo "  make conversation       - Run the conversation mode"
	@echo ""
	@echo "Testing commands:"
	@echo "  make test-dummy         - Create a dummy sine wave file and transcribe it"
	@echo "  make test-dummy-speech  - Create a dummy speech file with text and transcribe it"
	@echo "  make test-dummy-en      - Create a dummy speech file and transcribe with English language"
	@echo ""
	@echo "Transcription commands:"
	@echo "  make transcribe FILE=path - Transcribe a specific audio file (alias for test-file)"
	@echo "  make transcribe-en FILE=path - Transcribe a file with English language"
	@echo "  make transcribe-model FILE=path MODEL=model - Transcribe with specific model"
	@echo "  make test-file FILE=path - Transcribe a specific audio file"
	@echo "  make test-file-en FILE=path - Transcribe a file with English language"
	@echo "  make test-file-model FILE=path MODEL=model - Transcribe with specific model"
	@echo "  make test-dir DIR=path   - Transcribe all WAV files in a directory"
	@echo "  make test-dir-en DIR=path - Transcribe all files in directory with English"
	@echo "  make test-dir-model DIR=path MODEL=model - Transcribe directory with model"
	@echo ""
	@echo "Test data generation:"
	@echo "  make test-suite         - Create a comprehensive test suite of audio samples"
	@echo "  make test-languages     - Create samples in multiple languages"
	@echo ""
	@echo "Seed functionality commands:"
	@echo "  make test-seed-sine     - Create a sine wave audio file using seed functionality"
	@echo "  make test-seed-speech   - Create a speech audio file using seed functionality"
	@echo "  make test-seed-multi    - Create multi-language samples using seed functionality"
	@echo "  make test-seed-suite    - Create a comprehensive test suite using seed functionality"
	@echo ""

setup:
	@echo "Setting up environment..."
	$(PYTHON) -m venv $(VENV)
	. $(VENV)/bin/activate && $(PIP) install -r requirements.txt
	@echo "Setup complete. Use 'make local-run' to run the app locally"

docker-run:
	@echo "Running app in Docker..."
	docker-compose up

docker-build:
	@echo "Building Docker image..."
	docker-compose build

docker-stop:
	@echo "Stopping Docker containers..."
	docker-compose down --volumes

local-run:
	@echo "Running app locally..."
	@if [ ! -d "$(VENV)" ]; then \
		echo "Virtual environment not found. Running setup first..."; \
		$(MAKE) setup; \
	fi
	. $(VENV)/bin/activate && AUDIO_INPUT_DIR=$(PWD)/input $(PYTHON) -m audio

clean:
	@echo "Cleaning up..."
	docker-compose down --rmi local
	rm -rf $(VENV)
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "Cleanup complete"

# Command-line pipeline commands

audio-in:
	@echo "Running audio-in pipeline..."
	@if [ ! -d "$(VENV)" ]; then \
		echo "Virtual environment not found. Running setup first..."; \
		$(MAKE) setup; \
	fi
	. $(VENV)/bin/activate && $(PYTHON) -m audio audio-in

audio-out:
	@echo "Running audio-out pipeline..."
	@if [ ! -d "$(VENV)" ]; then \
		echo "Virtual environment not found. Running setup first..."; \
		$(MAKE) setup; \
	fi
	. $(VENV)/bin/activate && $(PYTHON) -m audio audio-out --data-source "This is a test of the text-to-speech functionality."

conversation:
	@echo "Starting conversation mode..."
	@if [ ! -d "$(VENV)" ]; then \
		echo "Virtual environment not found. Running setup first..."; \
		$(MAKE) setup; \
	fi
	. $(VENV)/bin/activate && $(PYTHON) -m audio conversation

# Testing commands for dummy files and transcription

test-dummy:
	@echo "Creating and transcribing a dummy sine wave file..."
	@if [ ! -d "$(VENV)" ]; then \
		echo "Virtual environment not found. Running setup first..."; \
		$(MAKE) setup; \
	fi
	. $(VENV)/bin/activate && $(PYTHON) dummy/create_dummy_file.py --output input/dummy_sine.wav
	. $(VENV)/bin/activate && $(PYTHON) -m audio audio-in --file input/dummy_sine.wav

test-dummy-speech:
	@echo "Creating and transcribing a dummy speech file..."
	@if [ ! -d "$(VENV)" ]; then \
		echo "Virtual environment not found. Running setup first..."; \
		$(MAKE) setup; \
	fi
	. $(VENV)/bin/activate && $(PYTHON) dummy/create_dummy_file.py --text "This is a test of the audio transcription system." --output input/dummy_speech.wav
	. $(VENV)/bin/activate && $(PYTHON) -m audio audio-in --file input/dummy_speech.wav

test-dummy-en:
	@echo "Creating and transcribing a dummy speech file with English language specified..."
	@if [ ! -d "$(VENV)" ]; then \
		echo "Virtual environment not found. Running setup first..."; \
		$(MAKE) setup; \
	fi
	. $(VENV)/bin/activate && $(PYTHON) dummy/create_dummy_file.py --text "This is a test of the audio transcription system." --output input/dummy_speech.wav
	. $(VENV)/bin/activate && $(PYTHON) -m audio audio-in --file input/dummy_speech.wav --language en

test-file:
	@echo "Transcribing file: $(FILE)"
	@if [ -z "$(FILE)" ]; then \
		echo "Error: Please specify a file with FILE=path"; \
		exit 1; \
	fi
	@if [ ! -d "$(VENV)" ]; then \
		echo "Virtual environment not found. Running setup first..."; \
		$(MAKE) setup; \
	fi
	. $(VENV)/bin/activate && $(PYTHON) -m audio audio-in --file $(FILE)

test-dir:
	@echo "Transcribing all WAV files in directory: $(DIR)"
	@if [ -z "$(DIR)" ]; then \
		echo "Error: Please specify a directory with DIR=path"; \
		exit 1; \
	fi
	@if [ ! -d "$(VENV)" ]; then \
		echo "Virtual environment not found. Running setup first..."; \
		$(MAKE) setup; \
	fi
	. $(VENV)/bin/activate && $(PYTHON) -m audio audio-in --dir $(DIR)

# Additional test commands with language specification

test-file-en:
	@echo "Transcribing file with English language: $(FILE)"
	@if [ -z "$(FILE)" ]; then \
		echo "Error: Please specify a file with FILE=path"; \
		exit 1; \
	fi
	@if [ ! -d "$(VENV)" ]; then \
		echo "Virtual environment not found. Running setup first..."; \
		$(MAKE) setup; \
	fi
	. $(VENV)/bin/activate && $(PYTHON) -m audio audio-in --file $(FILE) --language en

test-dir-en:
	@echo "Transcribing all WAV files in directory with English language: $(DIR)"
	@if [ -z "$(DIR)" ]; then \
		echo "Error: Please specify a directory with DIR=path"; \
		exit 1; \
	fi
	@if [ ! -d "$(VENV)" ]; then \
		echo "Virtual environment not found. Running setup first..."; \
		$(MAKE) setup; \
	fi
	. $(VENV)/bin/activate && $(PYTHON) -m audio audio-in --dir $(DIR) --language en

# Convenient aliases for transcription commands

transcribe:
	@echo "Transcribing file: $(FILE)"
	@if [ -z "$(FILE)" ]; then \
		echo "Error: Please specify a file with FILE=path"; \
		exit 1; \
	fi
	@if [ ! -d "$(VENV)" ]; then \
		echo "Virtual environment not found. Running setup first..."; \
		$(MAKE) setup; \
	fi
	. $(VENV)/bin/activate && $(PYTHON) -m audio audio-in --file $(FILE)

transcribe-en:
	@echo "Transcribing file with English language: $(FILE)"
	@if [ -z "$(FILE)" ]; then \
		echo "Error: Please specify a file with FILE=path"; \
		exit 1; \
	fi
	@if [ ! -d "$(VENV)" ]; then \
		echo "Virtual environment not found. Running setup first..."; \
		$(MAKE) setup; \
	fi
	. $(VENV)/bin/activate && $(PYTHON) -m audio audio-in --file $(FILE) --language en

transcribe-model:
	@echo "Transcribing file with model $(MODEL): $(FILE)"
	@if [ -z "$(FILE)" ]; then \
		echo "Error: Please specify a file with FILE=path"; \
		exit 1; \
	fi
	@if [ -z "$(MODEL)" ]; then \
		echo "Error: Please specify a model with MODEL=tiny|base|small|medium|large"; \
		exit 1; \
	fi
	@if [ ! -d "$(VENV)" ]; then \
		echo "Virtual environment not found. Running setup first..."; \
		$(MAKE) setup; \
	fi
	. $(VENV)/bin/activate && $(PYTHON) -m audio audio-in --file $(FILE) --model $(MODEL)

# Additional test commands with model specification

test-file-model:
	@echo "Transcribing file with model $(MODEL): $(FILE)"
	@if [ -z "$(FILE)" ]; then \
		echo "Error: Please specify a file with FILE=path"; \
		exit 1; \
	fi
	@if [ -z "$(MODEL)" ]; then \
		echo "Error: Please specify a model with MODEL=tiny|base|small|medium|large"; \
		exit 1; \
	fi
	@if [ ! -d "$(VENV)" ]; then \
		echo "Virtual environment not found. Running setup first..."; \
		$(MAKE) setup; \
	fi
	. $(VENV)/bin/activate && $(PYTHON) -m audio audio-in --file $(FILE) --model $(MODEL)

test-dir-model:
	@echo "Transcribing all WAV files in directory with model $(MODEL): $(DIR)"
	@if [ -z "$(DIR)" ]; then \
		echo "Error: Please specify a directory with DIR=path"; \
		exit 1; \
	fi
	@if [ -z "$(MODEL)" ]; then \
		echo "Error: Please specify a model with MODEL=tiny|base|small|medium|large"; \
		exit 1; \
	fi
	@if [ ! -d "$(VENV)" ]; then \
		echo "Virtual environment not found. Running setup first..."; \
		$(MAKE) setup; \
	fi
	. $(VENV)/bin/activate && $(PYTHON) -m audio audio-in --dir $(DIR) --model $(MODEL)

# Advanced test suite generation with seed functionality

test-seed-suite:
	@echo "Creating a comprehensive test suite using seed functionality..."
	@if [ ! -d "$(VENV)" ]; then \
		echo "Virtual environment not found. Running setup first..."; \
		$(MAKE) setup; \
	fi
	. $(VENV)/bin/activate && $(PYTHON) -m audio --seed --seed-type test-suite

# Legacy test suite generation
test-suite:
	@echo "Creating a comprehensive test suite of audio samples..."
	@if [ ! -d "$(VENV)" ]; then \
		echo "Virtual environment not found. Running setup first..."; \
		$(MAKE) setup; \
	fi
	. $(VENV)/bin/activate && $(PYTHON) dummy/create_test_suite.py --output-dir input/test_suite

test-languages:
	@echo "Creating samples in multiple languages..."
	@if [ ! -d "$(VENV)" ]; then \
		echo "Virtual environment not found. Running setup first..."; \
		$(MAKE) setup; \
	fi
	. $(VENV)/bin/activate && $(PYTHON) dummy/create_multi_language_samples.py --output-dir input/language_samples

# Test commands for running unit and integration tests

run-audio-out:
	. $(VENV)/bin/activate && $(PYTHON) -m audio audio-out --data-source "$(DATA-SOURCE)" --play

run-audio-in:
	. $(VENV)/bin/activate && $(PYTHON) -m audio audio-in --record --output output/audio-input.txt

# Default
test: test-unit test-integration

# Unit tests only
test-unit:
	. $(VENV)/bin/activate && python -m pytest tests/unit

# Integration tests only
test-integration:
	. $(VENV)/bin/activate && python -m pytest tests/integration
