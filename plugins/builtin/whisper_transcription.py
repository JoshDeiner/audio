"""Built-in Whisper transcription plugin.

This module provides a transcription plugin that uses the Whisper model.
"""

import logging
import os
from typing import Dict, Optional

from faster_whisper import WhisperModel

from config.configuration_manager import ConfigurationManager
from plugins.transcription_plugin import TranscriptionPlugin
from services.exceptions import TranscriptionError

logger = logging.getLogger(__name__)


class WhisperTranscriptionPlugin(TranscriptionPlugin):
    """Whisper-based transcription plugin.

    This plugin uses the Whisper model from faster-whisper to transcribe audio.
    """
    
    @property
    def plugin_id(self) -> str:
        return "whisper_transcription"
    
    @property
    def plugin_name(self) -> str:
        return "Whisper Transcription"
    
    @property
    def plugin_version(self) -> str:
        return "1.0.0"
    
    def __init__(self) -> None:
        """Initialize the plugin."""
        self._model = None
        self._model_size = None
        self._compute_type = None
        self._device = None
        self._initialized = False
        self._supported_languages = self._get_whisper_languages()
    
    def initialize(self, config_manager: Optional[ConfigurationManager] = None) -> None:
        """Initialize the plugin with configuration.

        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager or ConfigurationManager
        
        # Get model configuration
        model_size = self.config_manager.get("WHISPER_MODEL", "tiny")
        compute_type = self.config_manager.get("WHISPER_COMPUTE_TYPE", "int8")
        device = self.config_manager.get("WHISPER_DEVICE", "cpu")
        
        # Initialize the model
        try:
            self._model = WhisperModel(
                model_size,
                device=device,
                compute_type=compute_type,
            )
            
            self._model_size = model_size
            self._compute_type = compute_type
            self._device = device
            self._initialized = True
            
            logger.info(f"Initialized Whisper model: {model_size} on {device}")
        except Exception as e:
            logger.error(f"Failed to initialize Whisper model: {e}")
            raise TranscriptionError(f"Failed to initialize Whisper model: {e}")
    
    def cleanup(self) -> None:
        """Clean up resources used by the plugin."""
        # Free up memory
        self._model = None
        self._initialized = False
        logger.info("Cleaned up Whisper transcription plugin")
    
    def transcribe(self, audio_path: str, language: Optional[str] = None, 
                   options: Optional[Dict] = None) -> str:
        """Transcribe audio file to text.

        Args:
            audio_path: Path to the audio file
            language: Optional language code
            options: Additional options for the transcription engine

        Returns:
            str: Transcribed text

        Raises:
            TranscriptionError: If transcription fails
        """
        if not self._initialized or self._model is None:
            raise TranscriptionError("Whisper model not initialized")
            
        if not os.path.exists(audio_path):
            raise TranscriptionError(f"Audio file not found: {audio_path}")
        
        try:
            # Set up transcription parameters
            transcription_options = options or {}
            
            # Add beam size if not specified
            if "beam_size" not in transcription_options:
                transcription_options["beam_size"] = 5
                
            # If language is specified, use it
            if language:
                transcription_options["language"] = language
                logger.info(f"Using specified language: {language}")
            
            # Run transcription
            segments, info = self._model.transcribe(audio_path, **transcription_options)
            
            # Collect transcription segments
            transcription = " ".join([segment.text for segment in segments])
            
            # Log information
            detected_lang = info.language
            if language:
                logger.info(f"Transcription complete using language: {language}")
            else:
                logger.info(
                    f"Transcription complete (detected language: {detected_lang}, "
                    f"probability: {info.language_probability:.2f})"
                )
                
            return transcription.strip()
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            raise TranscriptionError(f"Failed to transcribe audio: {str(e)}")
    
    def supports_language(self, language_code: str) -> bool:
        """Check if this plugin supports the given language.

        Args:
            language_code: ISO language code

        Returns:
            bool: True if supported, False otherwise
        """
        return language_code in self._supported_languages
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get all supported languages.

        Returns:
            Dict mapping language codes to language names
        """
        return self._supported_languages
    
    def get_model_info(self) -> Dict:
        """Get information about the transcription model.

        Returns:
            Dict with model information
        """
        return {
            "model_type": "Whisper",
            "model_size": self._model_size,
            "compute_type": self._compute_type,
            "device": self._device,
            "language_count": len(self._supported_languages),
        }
    
    def _get_whisper_languages(self) -> Dict[str, str]:
        """Get the supported languages for Whisper.

        Returns:
            Dict mapping language codes to language names
        """
        # This is a subset of languages supported by Whisper
        return {
            "en": "English",
            "zh": "Chinese",
            "de": "German",
            "es": "Spanish",
            "ru": "Russian",
            "ko": "Korean",
            "fr": "French",
            "ja": "Japanese",
            "pt": "Portuguese",
            "tr": "Turkish",
            "pl": "Polish",
            "ca": "Catalan",
            "nl": "Dutch",
            "ar": "Arabic",
            "sv": "Swedish",
            "it": "Italian",
            "id": "Indonesian",
            "hi": "Hindi",
            "fi": "Finnish",
            "vi": "Vietnamese",
            "he": "Hebrew",
            "uk": "Ukrainian",
            "el": "Greek",
            "ms": "Malay",
            "cs": "Czech",
            "ro": "Romanian",
            "da": "Danish",
            "hu": "Hungarian",
            "ta": "Tamil",
            "no": "Norwegian",
            "th": "Thai",
            "ur": "Urdu",
            "hr": "Croatian",
            "bg": "Bulgarian",
            "lt": "Lithuanian",
            "la": "Latin",
            "mi": "Maori",
            "ml": "Malayalam",
            "cy": "Welsh",
            "sk": "Slovak",
            "te": "Telugu",
            "fa": "Persian",
            "lv": "Latvian",
            "bn": "Bengali",
            "sr": "Serbian",
            "az": "Azerbaijani",
            "sl": "Slovenian",
            "kn": "Kannada",
            "et": "Estonian",
            "mk": "Macedonian",
            "br": "Breton",
            "eu": "Basque",
            "is": "Icelandic",
            "hy": "Armenian",
            "ne": "Nepali",
            "mn": "Mongolian",
            "bs": "Bosnian",
            "kk": "Kazakh",
            "sq": "Albanian",
            "sw": "Swahili",
            "gl": "Galician",
            "mr": "Marathi",
            "pa": "Punjabi",
            "si": "Sinhala",
            "km": "Khmer",
            "sn": "Shona",
            "yo": "Yoruba",
            "so": "Somali",
            "af": "Afrikaans",
            "oc": "Occitan",
            "ka": "Georgian",
            "be": "Belarusian",
            "tg": "Tajik",
            "sd": "Sindhi",
            "gu": "Gujarati",
            "am": "Amharic",
            "yi": "Yiddish",
            "lo": "Lao",
            "uz": "Uzbek",
            "fo": "Faroese",
            "ht": "Haitian Creole",
            "ps": "Pashto",
            "tk": "Turkmen",
            "nn": "Nynorsk",
            "mt": "Maltese",
            "sa": "Sanskrit",
            "lb": "Luxembourgish",
            "my": "Myanmar",
            "bo": "Tibetan",
            "tl": "Tagalog",
            "mg": "Malagasy",
            "as": "Assamese",
            "tt": "Tatar",
            "haw": "Hawaiian",
            "ln": "Lingala",
            "ha": "Hausa",
            "ba": "Bashkir",
            "jw": "Javanese",
            "su": "Sundanese",
        }