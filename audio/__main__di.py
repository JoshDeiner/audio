"""Main entry point for the audio package with DI support.

This module provides the main function that bootstraps the DI container
and runs the application with proper dependency injection.

Author: Claude Code
Created: 2025-04-27
"""

import logging
import sys

from audio.application_enhanced import main

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    # Forward to application main function
    sys.exit(main())
