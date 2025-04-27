"""Service factory for the audio application.

This module provides factory functions for creating services,
allowing for dependency injection and plugin-based implementation.
"""

import logging
from typing import Any, Dict, Optional, Type

from config.configuration_manager import ConfigurationManager
from plugins.plugin_manager import PluginManager
from services.audio_playback_service import AudioPlaybackService
from services.audio_service import AudioRecordingService
from services.base_service_with_config import BaseService
from services.file_service import FileService
from services.text_to_speech_service import TextToSpeechService
from services.transcription_service import TranscriptionService

logger = logging.getLogger(__name__)


class ServiceFactory:
    """Factory for creating service instances.

    This class provides methods for creating and configuring service instances,
    potentially using plugins for implementation.
    """

    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ServiceFactory, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
        
    def __init__(self, config_manager: Optional[ConfigurationManager] = None):
        """Initialize the service factory.

        Args:
            config_manager: Optional configuration manager instance
        """
        # Only initialize once (singleton pattern)
        if getattr(self, '_initialized', False):
            return
            
        self.config_manager = config_manager or ConfigurationManager
        self.plugin_manager = PluginManager(self.config_manager)
        self._initialized = True
        
    def initialize(self) -> None:
        """Initialize the service factory."""
        # Initialize plugin manager if not already done
        self.plugin_manager.initialize()
        logger.info("Service factory initialized")
        
    def create_transcription_service(self, config: Optional[Dict[str, Any]] = None) -> TranscriptionService:
        """Create a transcription service.

        Args:
            config: Optional configuration dictionary

        Returns:
            TranscriptionService instance
        """
        # Create the service with plugin-aware implementation
        service = TranscriptionService(self.config_manager)
        
        # Set up with plugin if available
        plugin_id = None
        if config and 'transcription_plugin' in config:
            plugin_id = config['transcription_plugin']
            
        # Get the plugin from manager
        plugin = self.plugin_manager.get_transcription_plugin(plugin_id)
        
        # If we have a plugin, set it on the service
        if plugin:
            service.set_plugin(plugin)
        
        return service
        
    def create_file_service(self) -> FileService:
        """Create a file service.

        Returns:
            FileService instance
        """
        service = FileService(self.config_manager)
        
        # Set up with plugins if available
        format_plugin = self.plugin_manager.get_audio_format_plugin()
        if format_plugin:
            service.set_format_plugin(format_plugin)
            
        return service
        
    def create_audio_recording_service(self) -> AudioRecordingService:
        """Create an audio recording service.

        Returns:
            AudioRecordingService instance
        """
        return AudioRecordingService(self.config_manager)
        
    def create_audio_playback_service(self) -> AudioPlaybackService:
        """Create an audio playback service.

        Returns:
            AudioPlaybackService instance
        """
        return AudioPlaybackService(self.config_manager)
        
    def create_tts_service(self) -> TextToSpeechService:
        """Create a text-to-speech service.

        Returns:
            TextToSpeechService instance
        """
        return TextToSpeechService(self.config_manager)
        
    def create_service(self, service_class: Type[BaseService], **kwargs) -> BaseService:
        """Create a service of the specified class.

        Args:
            service_class: Class of service to create
            **kwargs: Additional arguments to pass to constructor

        Returns:
            Service instance
        """
        # Create service with config manager
        service = service_class(self.config_manager, **kwargs)
        
        # Initialize if required
        if hasattr(service, 'initialize') and callable(service.initialize):
            service.initialize()
            
        return service
        
    def cleanup(self) -> None:
        """Clean up resources."""
        # Clean up plugin manager
        self.plugin_manager.cleanup()
        logger.info("Service factory cleaned up")