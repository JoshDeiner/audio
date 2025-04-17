.PHONY: help setup docker-run local-run docker-build docker-stop clean

# Default Python interpreter and pip
PYTHON := python3
PIP := pip3
VENV := venv

help:
	@echo "Audio Recording App Makefile"
	@echo ""
	@echo "Available commands:"
	@echo "  make setup         - Install dependencies and create virtual environment"
	@echo "  make docker-run    - Run the application in Docker"
	@echo "  make local-run     - Run the application locally"
	@echo "  make docker-build  - Rebuild the Docker image"
	@echo "  make docker-stop   - Stop any running Docker containers"
	@echo "  make clean         - Remove temporary files and virtual environment"
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
	. $(VENV)/bin/activate && AUDIO_INPUT_DIR=$(PWD)/input $(PYTHON) transcriber.py

clean:
	@echo "Cleaning up..."
	docker-compose down --rmi local
	rm -rf $(VENV)
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "Cleanup complete"
