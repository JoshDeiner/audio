import os
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class ConfigurationManager:
    """Centralized configuration manager for the audio application."""
    
    # Default configuration values
    _defaults = {
        # Paths
        "AUDIO_INPUT_DIR": "input",
        "AUDIO_OUTPUT_DIR": "output",
        
        # Whisper configuration
        "WHISPER_MODEL": "tiny",
        "WHISPER_COMPUTE_TYPE": "int8",
        "WHISPER_DEVICE": "cpu",
        
        # Platform configuration
        "AUDIO_DRIVER": "",
        "PLATFORM": "",
    }
    
    # Configuration store
    _config: Dict[str, Any] = {}
    
    @classmethod
    def initialize(cls, config_file: Optional[str] = None) -> None:
        """Initialize configuration from environment variables and optional config file.
        
        Args:
            config_file: Optional path to configuration file
        """
        # Start with defaults
        cls._config = cls._defaults.copy()
        
        # Override with environment variables
        for key in cls._defaults:
            if key in os.environ:
                cls._config[key] = os.environ[key]
                
        # Override with config file if provided
        if config_file and os.path.exists(config_file):
            cls._load_from_file(config_file)
            
        # Ensure critical directories exist
        cls._ensure_directories()
        
        logger.info("Configuration initialized")
        
    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """Get configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        return cls._config.get(key, default)
        
    @classmethod
    def set(cls, key: str, value: Any) -> None:
        """Set configuration value.
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        cls._config[key] = value
        
    @classmethod
    def _load_from_file(cls, config_file: str) -> None:
        """Load configuration from file.
        
        Args:
            config_file: Path to configuration file
        """
        try:
            # Simple implementation for env file format
            with open(config_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        key, value = line.split("=", 1)
                        cls._config[key.strip()] = value.strip()
        except Exception as e:
            logger.error(f"Error loading configuration file: {e}")
            
    @classmethod
    def _ensure_directories(cls) -> None:
        """Ensure required directories exist."""
        for dir_key in ["AUDIO_INPUT_DIR", "AUDIO_OUTPUT_DIR"]:
            dir_path = cls._config.get(dir_key)
            if dir_path and not os.path.exists(dir_path):
                try:
                    os.makedirs(dir_path, exist_ok=True)
                    logger.info(f"Created directory: {dir_path}")
                except Exception as e:
                    logger.error(f"Failed to create directory {dir_path}: {e}")