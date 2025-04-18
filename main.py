#!/usr/bin/env python3
"""Audio transcription main entry point.

This module provides the main entry point for the audio transcription tool,
allowing users to record audio and transcribe it using the faster-whisper model.
"""
import logging
import sys
from typing import Tuple

from colorama import Fore, Style, init  # type: ignore
from dotenv import load_dotenv

from services.application_service import ApplicationService
from services.exceptions import AudioServiceError

# Load environment variables from .env file
load_dotenv()

# Initialize colorama with strip=False for compatibility with Docker/TTY
init(strip=False)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main() -> Tuple[str, str]:
    """Main entry point for the transcription tool.
    
    Returns:
        Tuple[str, str]: Paths to the audio file and transcript file
        
    Raises:
        SystemExit: If an error occurs during execution
    """
    try:
        app_service = ApplicationService()
        return app_service.run()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Process interrupted by user.{Style.RESET_ALL}")
        sys.exit(0)
    except AudioServiceError as e:
        print(f"\n{Fore.RED}Error: {e}{Style.RESET_ALL}")
        logger.error(f"Application error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Fore.RED}Unexpected error: {e}{Style.RESET_ALL}")
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
