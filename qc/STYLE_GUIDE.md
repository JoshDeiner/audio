# Python Style Guide for Audio Transcription Services

This style guide extends the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html) with specific conventions for our audio transcription service architecture.

## Table of Contents
- [Naming Conventions](#naming-conventions)
- [Documentation Standards](#documentation-standards)
- [Code Organization](#code-organization)
- [Error Handling](#error-handling)
- [Type Annotations](#type-annotations)
- [Imports](#imports)

## Naming Conventions

### General Naming

Follow standard Python naming conventions:
- `snake_case` for variables, functions, methods, modules, and packages
- `PascalCase` for classes and exceptions
- `UPPER_SNAKE_CASE` for constants

### Service-Specific Naming

#### Service Modules and Classes
- Service module names should be descriptive and end with `_service`: `transcription_service.py`, `audio_processing_service.py`
- Service classes should be named with a `Service` suffix: `TranscriptionService`, `AudioProcessingService`

#### Client Classes
- Client classes should be named with a `Client` suffix: `TranscriptionServiceClient`, `AudioProcessingClient`

#### Message Handlers
- Message handler functions should be prefixed with `handle_`: `handle_transcription_request`, `handle_audio_chunk`
- Event handlers should be prefixed with `on_`: `on_transcription_complete`, `on_audio_received`

#### Commands and Queries (CQRS)
- Commands should be named with a verb in imperative form: `TranscribeAudioCommand`, `ProcessChunkCommand`
- Queries should be named with a descriptive noun or adjective: `TranscriptionStatusQuery`, `AudioMetadataQuery`

#### Events
- Events should be named in past tense: `AudioRecorded`, `TranscriptionCompleted`, `ChunkProcessed`

## Documentation Standards

### Module Documentation
Every module should have a docstring that includes:
- Brief description of the module's purpose
- Any important notes about usage
- Author information and creation date

```python
"""
Audio transcription service module.

This module provides functionality for transcribing audio files using the
faster-whisper model in a service-oriented architecture.

Author: Your Name
Created: YYYY-MM-DD
"""
```

### Service Interface Documentation
Service interfaces must be thoroughly documented:

```python
class TranscriptionService:
    """
    Service for transcribing audio files.
    
    This service handles the processing of audio files and returns
    transcribed text using the faster-whisper model.
    
    Attributes:
        model: The whisper model instance
        compute_type: The computation type (float16, float32)
        device: The device to use for computation (cpu, cuda)
    """
    
    def transcribe(self, audio_path: str, language: Optional[str] = None) -> TranscriptionResult:
        """
        Transcribe an audio file to text.
        
        Args:
            audio_path: Path to the audio file to transcribe
            language: Optional language code to use for transcription
            
        Returns:
            TranscriptionResult object containing the transcribed text and metadata
            
        Raises:
            FileNotFoundError: If the audio file does not exist
            TranscriptionError: If the transcription process fails
            
        Example:
            ```python
            service = TranscriptionService()
            result = service.transcribe("path/to/audio.wav")
            print(result.text)
            ```
        """
```

### API Documentation
Public APIs should include:
- Function/method purpose
- Parameter descriptions with types
- Return value descriptions with types
- Exceptions that might be raised
- Usage examples

## Code Organization

### File Structure
- One class per file for major components
- Related utilities can be grouped in a single file
- Keep files under 500 lines; split if necessary

### Class Structure
Order class contents as follows:
1. Class docstring
2. Class attributes and constants
3. `__init__` and other special methods
4. Public methods
5. Protected methods (prefixed with `_`)
6. Private methods (prefixed with `__`)
7. Static and class methods
8. Properties

## Error Handling

### Exception Hierarchy
Create a custom exception hierarchy for your services:

```python
class AudioServiceError(Exception):
    """Base exception for all audio service errors."""
    pass

class TranscriptionError(AudioServiceError):
    """Raised when transcription fails."""
    pass

class AudioProcessingError(AudioServiceError):
    """Raised when audio processing fails."""
    pass
```

### Error Handling Patterns for Distributed Operations

1. **Use Specific Exceptions**: Create domain-specific exceptions that can be properly handled by clients.

2. **Include Context**: Always include relevant context in exceptions:

```python
try:
    # Some operation
except SomeError as e:
    raise TranscriptionError(f"Failed to transcribe audio {audio_id}: {str(e)}") from e
```

3. **Error Codes**: Use error codes for machine-readable error handling:

```python
class TranscriptionError(AudioServiceError):
    """Raised when transcription fails."""
    
    def __init__(self, message, error_code=None, details=None):
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {}
```

4. **Retry Patterns**: Document which operations are idempotent and can be safely retried:

```python
@retry(
    retry=retry_if_exception_type(TransientError),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def process_audio_chunk(chunk_data):
    """Process an audio chunk with retry for transient errors."""
    # Implementation
```

5. **Circuit Breaker**: Implement circuit breakers for external service calls:

```python
@circuit(failure_threshold=5, recovery_timeout=30)
def call_external_transcription_service(audio_data):
    """Call external transcription service with circuit breaker pattern."""
    # Implementation
```

## Type Annotations

Use type annotations for all function definitions:

```python
def process_audio(
    audio_path: str,
    sample_rate: int = 16000,
    channels: int = 1
) -> AudioProcessingResult:
    """Process audio file."""
    # Implementation
```

Use typing module for complex types:

```python
from typing import Dict, List, Optional, Union, Callable

AudioChunk = Dict[str, Union[bytes, int, float]]
TranscriptionCallback = Callable[[str, float], None]

def process_chunks(
    chunks: List[AudioChunk],
    callback: Optional[TranscriptionCallback] = None
) -> List[str]:
    """Process audio chunks."""
    # Implementation
```

## Imports

Follow isort conventions with these sections:
1. Standard library imports
2. Related third-party imports
3. Local application/library specific imports

```python
# Standard library
import os
import sys
from typing import Dict, List, Optional

# Third-party
import numpy as np
from faster_whisper import WhisperModel

# Local
from audio.core.models import AudioChunk
from audio.services.base import BaseService
```
