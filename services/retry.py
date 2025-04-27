"""Retry pattern implementation for services.

This module provides utility decorators for implementing retry logic
for operations that might fail transiently.

Author: Claude Code
Created: 2025-04-27
"""

import functools
import logging
import time
from typing import Any, Callable, Optional, Type, TypeVar, Union, cast

from services.exceptions import AudioServiceError

logger = logging.getLogger(__name__)

T = TypeVar("T")


def retry(
    max_attempts: int = 3,
    retry_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: Union[Type[Exception], tuple] = AudioServiceError,
    error_code: Optional[str] = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator for retrying operations that fail transiently.
    
    Args:
        max_attempts: Maximum number of attempts before giving up
        retry_delay: Initial delay between retries in seconds
        backoff_factor: Multiplication factor for delay after each failure
        exceptions: Exception type(s) to catch and retry on
        error_code: Optional error code to check for (only for AudioServiceError)
        
    Returns:
        Decorator function that implements retry logic
        
    Example:
        ```python
        @retry(max_attempts=3, exceptions=TranscriptionError)
        def transcribe_audio(audio_path: str) -> str:
            # Implementation that might fail transiently
        ```
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            delay = retry_delay
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                    
                except exceptions as e:
                    # Check error code if specified
                    if error_code and isinstance(e, AudioServiceError):
                        if getattr(e, "error_code", None) != error_code:
                            # Not the specific error we want to retry on
                            raise
                    
                    last_exception = e
                    
                    # Log retry attempt
                    if attempt < max_attempts - 1:
                        logger.warning(
                            f"Retry {attempt+1}/{max_attempts} for {func.__name__}: {e}"
                        )
                        
                        # Delay with exponential backoff
                        time.sleep(delay)
                        delay *= backoff_factor
                    else:
                        logger.error(
                            f"Failed after {max_attempts} attempts: {func.__name__}"
                        )
            
            # If we get here, all attempts failed
            if last_exception:
                raise last_exception
                
            # Should never happen, but keep type checker happy
            raise RuntimeError(f"Unexpected error in retry mechanism for {func.__name__}")
            
        return cast(Callable[..., T], wrapper)
    
    return decorator


def circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: int = 60,
    exceptions: Union[Type[Exception], tuple] = Exception,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator for implementing the circuit breaker pattern.
    
    Args:
        failure_threshold: Number of failures before opening the circuit
        recovery_timeout: Time in seconds to wait before trying to close circuit
        exceptions: Exception type(s) to count as failures
        
    Returns:
        Decorator function that implements circuit breaker logic
        
    Example:
        ```python
        @circuit_breaker(failure_threshold=3, recovery_timeout=30)
        def call_external_service() -> dict:
            # Implementation that calls external service
        ```
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        # Circuit state
        failures = 0
        circuit_open = False
        last_failure_time = 0.0
        
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            nonlocal failures, circuit_open, last_failure_time
            
            # Check if circuit is open
            if circuit_open:
                current_time = time.time()
                if current_time - last_failure_time > recovery_timeout:
                    # Try to close the circuit (half-open state)
                    logger.info(f"Attempting to close circuit for {func.__name__}")
                    circuit_open = False
                else:
                    # Circuit still open, fail fast
                    raise AudioServiceError(
                        f"Circuit breaker open for {func.__name__}",
                        error_code="CIRCUIT_OPEN"
                    )
            
            try:
                # Call the function
                result = func(*args, **kwargs)
                
                # Success, reset failure count
                if failures > 0:
                    logger.info(f"Circuit reset for {func.__name__}")
                    failures = 0
                    circuit_open = False
                
                return result
                
            except exceptions as e:
                # Increment failure count
                failures += 1
                last_failure_time = time.time()
                
                # Check if we should open the circuit
                if failures >= failure_threshold:
                    circuit_open = True
                    logger.warning(
                        f"Circuit breaker opened for {func.__name__} after {failures} failures"
                    )
                
                # Re-raise the exception
                raise
                
        return cast(Callable[..., T], wrapper)
    
    return decorator