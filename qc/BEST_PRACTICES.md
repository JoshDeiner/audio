# Best Practices for Audio Transcription Services

This document outlines best practices for developing and maintaining the audio transcription service architecture.

## Table of Contents
- [Code Organization Principles](#code-organization-principles)
- [Project Structure](#project-structure)
- [Code Quality Patterns](#code-quality-patterns)
- [Resource Management](#resource-management)
- [Asynchronous Processing Patterns](#asynchronous-processing-patterns)
- [Testing Strategies](#testing-strategies)

## Code Organization Principles

### Service Boundaries

1. **Single Responsibility Principle**: Each service should have a single responsibility and reason to change.
   - Example: Separate audio recording from transcription processing

2. **Domain-Driven Design**: Organize code around business domains rather than technical concerns.
   - Example: `audio_capture`, `transcription`, `text_processing` as separate domains

3. **Cohesion and Coupling**: Maximize cohesion within services and minimize coupling between services.
   - High cohesion: Keep related functionality together
   - Low coupling: Minimize dependencies between services

### Layered Architecture

Organize each service with clear layers:

1. **API Layer**: Handles external requests and responses
2. **Service Layer**: Contains business logic
3. **Domain Layer**: Defines core domain models and business rules
4. **Infrastructure Layer**: Handles external dependencies and technical concerns

Example for transcription service:
```
transcription/
├── api/                # API endpoints, controllers
├── service/            # Business logic, orchestration
├── domain/             # Core models, business rules
└── infrastructure/     # Database access, external services
```

## Project Structure

### Modular Monolith Structure

Start with a modular monolith that can evolve into microservices:

```
audio_transcription/
├── core/                       # Shared core functionality
│   ├── __init__.py
│   ├── config.py               # Configuration management
│   ├── exceptions.py           # Common exceptions
│   └── models.py               # Shared domain models
│
├── services/                   # Service modules
│   ├── __init__.py
│   ├── audio_capture/          # Audio recording service
│   │   ├── __init__.py
│   │   ├── api.py              # Service API
│   │   ├── models.py           # Domain models
│   │   └── service.py          # Business logic
│   │
│   ├── transcription/          # Transcription service
│   │   ├── __init__.py
│   │   ├── api.py
│   │   ├── models.py
│   │   └── service.py
│   │
│   └── text_processing/        # Text processing service
│       ├── __init__.py
│       ├── api.py
│       ├── models.py
│       └── service.py
│
├── infrastructure/             # Shared infrastructure
│   ├── __init__.py
│   ├── database.py             # Database connections
│   ├── messaging.py            # Message bus implementation
│   └── storage.py              # File storage utilities
│
├── api/                        # External API
│   ├── __init__.py
│   ├── rest.py                 # REST API endpoints
│   └── websocket.py            # WebSocket endpoints
│
└── main.py                     # Application entry point
```

### Evolution to Microservices

When evolving to microservices:

1. **Extract services**: Move each service module to its own repository
2. **Define interfaces**: Create clear API contracts between services
3. **Implement messaging**: Replace direct calls with message-based communication
4. **Deploy independently**: Set up CI/CD pipelines for each service

## Code Quality Patterns

### Control Flow Patterns

1. **Guard Clauses**: Use early returns to reduce nesting and improve readability:

```python
# ❌ Avoid deep nesting
def process_audio(file_path):
    if os.path.exists(file_path):
        if file_path.endswith('.wav'):
            if os.path.getsize(file_path) > 0:
                # Process the file
                return process_result
            else:
                return "File is empty"
        else:
            return "Not a WAV file"
    else:
        return "File not found"

# ✅ Use guard clauses instead
def process_audio(file_path):
    # Guard clauses for validation
    if not os.path.exists(file_path):
        return "File not found"
    
    if not file_path.endswith('.wav'):
        return "Not a WAV file"
        
    if os.path.getsize(file_path) == 0:
        return "File is empty"
    
    # Main logic (only executes if all validations pass)
    return process_result
```

2. **Inversion of Conditions**: Prefer positive conditions for the main flow and negative conditions for guard clauses:

```python
# ❌ Avoid
def get_audio_driver():
    audio_driver = os.environ.get("AUDIO_DRIVER")
    if audio_driver:
        logger.info(f"Using audio driver: {audio_driver}")
        audio_driver = audio_driver.lower()
        if audio_driver in ("pulse", "alsa"):
            return audio_driver
    
    # Default fallback logic...

# ✅ Better
def get_audio_driver():
    audio_driver = os.environ.get("AUDIO_DRIVER")
    if not audio_driver:
        return get_default_driver()
        
    logger.info(f"Using audio driver: {audio_driver}")
    audio_driver = audio_driver.lower()
    
    if audio_driver not in ("pulse", "alsa"):
        return get_default_driver()
        
    return audio_driver
```

3. **Function Decomposition**: Break complex conditions into well-named functions:

```python
# ❌ Avoid complex conditions
if file.endswith('.wav') and os.path.getsize(file) > 0 and sample_rate == 16000:
    # Process file

# ✅ Better
def is_valid_audio_file(file_path, required_sample_rate):
    return (file_path.endswith('.wav') and 
            os.path.getsize(file_path) > 0 and 
            get_sample_rate(file_path) == required_sample_rate)

if is_valid_audio_file(file, 16000):
    # Process file
```

### Error Handling Patterns

1. **Specific Exceptions**: Catch specific exceptions rather than generic ones:

```python
# ❌ Avoid
try:
    process_audio(file_path)
except Exception as e:
    logger.error(f"Error: {e}")

# ✅ Better
try:
    process_audio(file_path)
except FileNotFoundError:
    logger.error(f"Audio file not found: {file_path}")
except PermissionError:
    logger.error(f"No permission to access file: {file_path}")
except ValueError as e:
    logger.error(f"Invalid audio format: {e}")
except Exception as e:
    logger.error(f"Unexpected error processing audio: {e}")
```

## Resource Management

### Audio File Handling

1. **Streaming Processing**: Process audio in chunks rather than loading entire files:

```python
def process_audio_stream(audio_stream, chunk_size=4096):
    """Process audio in chunks to minimize memory usage."""
    while chunk := audio_stream.read(chunk_size):
        yield process_chunk(chunk)
```

2. **Temporary Storage**: Use temporary storage for intermediate files:

```python
import tempfile
import os

def process_large_audio(audio_data):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
        temp_path = temp_file.name
        temp_file.write(audio_data)
    
    try:
        result = process_audio_file(temp_path)
        return result
    finally:
        os.unlink(temp_path)  # Clean up temporary file
```

3. **Resource Pooling**: Pool expensive resources like transcription models:

```python
class WhisperModelPool:
    """Pool of WhisperModel instances for efficient resource usage."""
    
    def __init__(self, model_name, pool_size=2):
        self.pool = [
            WhisperModel(model_name) for _ in range(pool_size)
        ]
        self.lock = threading.Lock()
    
    def acquire(self):
        """Get a model from the pool."""
        with self.lock:
            if not self.pool:
                # Wait for a model to be returned
                # Implementation depends on concurrency approach
                pass
            return self.pool.pop()
    
    def release(self, model):
        """Return a model to the pool."""
        with self.lock:
            self.pool.append(model)
```

### Distributed Resource Management

1. **Worker Scaling**: Scale workers based on queue length and resource availability:

```python
def adjust_worker_count(queue_length, current_workers, max_workers=10):
    """Adjust worker count based on queue length."""
    if queue_length > current_workers * 5 and current_workers < max_workers:
        return current_workers + 1
    elif queue_length < current_workers * 2 and current_workers > 1:
        return current_workers - 1
    return current_workers
```

2. **Resource Limits**: Set clear resource limits for each service:

```python
# Configuration for resource limits
TRANSCRIPTION_SERVICE_CONFIG = {
    "max_concurrent_jobs": 5,
    "max_audio_size_mb": 100,
    "max_processing_time_seconds": 300,
    "memory_limit_mb": 1024,
}
```

## Asynchronous Processing Patterns

### Task Queue Pattern

Use task queues for handling long-running transcription jobs:

```python
# Producer: Submit transcription job
def submit_transcription_job(audio_file_path):
    job_id = str(uuid.uuid4())
    job_data = {
        "job_id": job_id,
        "audio_path": audio_file_path,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat()
    }
    
    # Store job metadata
    db.jobs.insert_one(job_data)
    
    # Enqueue job for processing
    message_bus.publish(
        "transcription_jobs",
        {"job_id": job_id}
    )
    
    return job_id

# Consumer: Process transcription job
def process_transcription_job(message):
    job_id = message["job_id"]
    job = db.jobs.find_one({"job_id": job_id})
    
    if not job:
        logger.error(f"Job {job_id} not found")
        return
    
    try:
        # Update job status
        db.jobs.update_one(
            {"job_id": job_id},
            {"$set": {"status": "processing"}}
        )
        
        # Process the audio file
        result = transcription_service.transcribe(job["audio_path"])
        
        # Update job with result
        db.jobs.update_one(
            {"job_id": job_id},
            {
                "$set": {
                    "status": "completed",
                    "result": result.text,
                    "completed_at": datetime.utcnow().isoformat()
                }
            }
        )
        
        # Publish completion event
        message_bus.publish(
            "transcription_completed",
            {
                "job_id": job_id,
                "status": "completed"
            }
        )
    except Exception as e:
        logger.exception(f"Error processing job {job_id}")
        
        # Update job with error
        db.jobs.update_one(
            {"job_id": job_id},
            {
                "$set": {
                    "status": "failed",
                    "error": str(e),
                    "completed_at": datetime.utcnow().isoformat()
                }
            }
        )
        
        # Publish failure event
        message_bus.publish(
            "transcription_failed",
            {
                "job_id": job_id,
                "status": "failed",
                "error": str(e)
            }
        )
```

### Progress Reporting

Implement progress reporting for long-running transcription jobs:

```python
def transcribe_with_progress(audio_path, job_id):
    """Transcribe audio with progress reporting."""
    total_duration = get_audio_duration(audio_path)
    segments = []
    
    # Process audio in segments
    for i, segment in enumerate(transcription_model.transcribe(audio_path)):
        segments.append(segment)
        
        # Calculate and report progress
        current_time = segment.end
        progress = min(current_time / total_duration * 100, 100)
        
        # Update job progress
        db.jobs.update_one(
            {"job_id": job_id},
            {"$set": {"progress": progress}}
        )
        
        # Publish progress event
        message_bus.publish(
            "transcription_progress",
            {
                "job_id": job_id,
                "progress": progress
            }
        )
    
    return combine_segments(segments)
```

### Backpressure Handling

Implement backpressure mechanisms to prevent system overload:

```python
class RateLimitedQueue:
    """Queue with rate limiting to prevent overload."""
    
    def __init__(self, max_items=100, process_rate=10):
        self.queue = queue.Queue(maxsize=max_items)
        self.process_rate = process_rate  # items per second
        self.last_processed = time.time()
    
    def put(self, item, block=True, timeout=None):
        """Put an item in the queue with backpressure."""
        return self.queue.put(item, block=block, timeout=timeout)
    
    def get(self, block=True, timeout=None):
        """Get an item from the queue with rate limiting."""
        item = self.queue.get(block=block, timeout=timeout)
        
        # Apply rate limiting
        now = time.time()
        time_since_last = now - self.last_processed
        target_interval = 1.0 / self.process_rate
        
        if time_since_last < target_interval:
            time.sleep(target_interval - time_since_last)
        
        self.last_processed = time.time()
        return item
```

## Testing Strategies

### Service Component Testing

1. **Unit Testing**: Test individual components in isolation with mocked dependencies
2. **Integration Testing**: Test interaction between components within a service
3. **Service Testing**: Test the service as a whole with mocked external dependencies

### Service Integration Testing

1. **Contract Testing**: Verify that services adhere to their API contracts
2. **End-to-End Testing**: Test the complete flow through all services
3. **Chaos Testing**: Test system resilience by simulating failures

### Testing Pyramid

Follow the testing pyramid approach:
- Many unit tests (fast, focused)
- Fewer integration tests (slower, broader)
- Few end-to-end tests (slowest, comprehensive)

### Test Data Management

1. **Test Fixtures**: Create reusable test fixtures for audio data
2. **Mock Services**: Use mock implementations for external services
3. **Test Environments**: Maintain isolated test environments
