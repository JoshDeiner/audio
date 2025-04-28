"""Platform detection service implementation for audio transcription tool."""

import logging
import os
import platform

from services.interfaces.platform_service_interface import (
    IPlatformDetectionService,
)

logger = logging.getLogger(__name__)


class PlatformDetectionService(IPlatformDetectionService):
    """Implementation for detecting platform and audio driver configuration."""

    def get_platform(self) -> str:
        """Detect platform and audio driver configuration.

        This method determines the platform or audio driver to use for audio recording.
        It checks for environment variables first, then falls back to auto-detection.

        Returns:
            str: Identifier for the platform or audio driver.
        """
        # Check for environment variable overrides first
        platform_from_env = self._get_platform_from_env()
        if platform_from_env:
            return platform_from_env

        # Auto-detect if not specified in environment
        return self._detect_platform_automatically()

    def _get_platform_from_env(self) -> str:
        """Get platform or audio driver from environment variables.

        Returns:
            str: Platform or audio driver identifier, or empty string if not found
        """
        # Check for audio driver override (highest priority)
        audio_driver = self._get_valid_audio_driver_from_env()
        if audio_driver:
            return audio_driver

        # Check for platform override (second priority)
        return self._get_platform_override_from_env()

    def _get_valid_audio_driver_from_env(self) -> str:
        """Get valid audio driver from environment variable.

        Returns:
            str: Valid audio driver name or empty string
        """
        audio_driver = os.environ.get("AUDIO_DRIVER", "").strip()

        # Return early if no audio driver specified
        if not audio_driver:
            return ""

        logger.info(f"Using audio driver from environment: {audio_driver}")
        audio_driver = audio_driver.lower()

        # Return early if not a recognized audio driver
        if audio_driver not in ("pulse", "alsa"):
            logger.debug(f"Unrecognized audio driver: {audio_driver}")
            return ""

        return audio_driver

    def _get_platform_override_from_env(self) -> str:
        """Get platform override from environment variable.

        Returns:
            str: Platform name or empty string
        """
        env_platform = os.environ.get("PLATFORM", "")
        if not env_platform:
            return ""

        return env_platform.lower()

    def _detect_platform_automatically(self) -> str:
        """Auto-detect platform based on system information.

        Returns:
            str: Detected platform identifier
        """
        sys_platform = platform.system().lower()

        if sys_platform == "linux":
            return self._detect_linux_platform()

        if sys_platform == "darwin":
            return "mac"

        if sys_platform.startswith("win"):
            return "win"

        return sys_platform

    def _detect_linux_platform(self) -> str:
        """Detect specific Linux platform or audio driver.

        Helper method to determine the specific Linux platform or audio driver.

        Returns:
            str: Linux platform identifier ("pi", "pulse", or "linux")
        """
        # Try to detect Raspberry Pi first
        pi_platform = self._check_for_raspberry_pi()
        if pi_platform:
            return pi_platform

        # Then check for PulseAudio
        pulse_platform = self._check_for_pulseaudio()
        if pulse_platform:
            return pulse_platform

        # Default to generic Linux
        return "linux"

    def _check_for_raspberry_pi(self) -> str:
        """Check if running on a Raspberry Pi.

        Returns:
            str: "pi" if running on Raspberry Pi, empty string otherwise
        """
        pi_model_path = "/proc/device-tree/model"

        if not os.path.exists(pi_model_path):
            return ""

        try:
            with open(pi_model_path) as f:
                model = f.read().lower()
                if "raspberry pi" not in model:
                    return ""
                return "pi"
        except (IOError, OSError) as e:
            logger.debug(f"Error reading Raspberry Pi model: {e}")
            return ""

    def _check_for_pulseaudio(self) -> str:
        """Check if PulseAudio is installed.

        Returns:
            str: "pulse" if PulseAudio is installed, empty string otherwise
        """
        pulse_paths = ["/usr/bin/pulseaudio", "/bin/pulseaudio"]

        try:
            if not any(os.path.exists(path) for path in pulse_paths):
                return ""
            return "pulse"
        except (IOError, OSError) as e:
            logger.debug(f"Error checking for PulseAudio: {e}")
            return ""
