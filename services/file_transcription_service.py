"""File-based transcription service for audio transcription tool."""
import logging
import multiprocessing
import os
from typing import List, Optional, Tuple

from colorama import Fore, Style  # type: ignore
from tqdm import tqdm  # type: ignore

from services.exceptions import FileOperationError
from services.file_service import FileService
from services.transcription_service import TranscriptionService

logger = logging.getLogger(__name__)


class FileTranscriptionService:
    """Service for transcribing audio files without recording."""

    def __init__(self):
        """Initialize the file transcription service."""
        self.file_service = FileService()
        self.transcription_service = TranscriptionService()

    def transcribe_file(
        self,
        file_path: str,
        model_size: Optional[str] = None,
        language: Optional[str] = None,
    ) -> str:
        """Transcribe a single audio file.

        Args:
            file_path: Path to the audio file
            model_size: Whisper model size (tiny, base, small, medium, large)
            language: Language code to use (e.g., 'en' for English).
                If provided, skips language detection.

        Returns:
            str: Path to the transcription file

        Raises:
            FileOperationError: If file operations fail
        """
        # Validate file path
        if not os.path.exists(file_path):
            raise FileOperationError(f"File not found: {file_path}")

        # Validate audio file
        if not self.file_service.validate_audio_file(file_path):
            raise FileOperationError(f"Invalid audio file: {file_path}")

        # Transcribe the file
        print(
            f"{Fore.CYAN}Transcribing file: {Fore.YELLOW}{file_path}{Style.RESET_ALL}"
        )
        transcription = self.transcription_service.transcribe_audio(
            file_path, model_size, language
        )

        # The transcription_service already saves the file and returns the text
        print(
            f"\n{Fore.GREEN}Transcription:{Style.RESET_ALL}\n{transcription}\n"
        )

        return transcription

    def _process_file(
        self, args: Tuple[str, Optional[str], Optional[str]]
    ) -> Tuple[str, Optional[str], Optional[Exception]]:
        """Process a single audio file with error handling.

        Args:
            args: Tuple containing (file_path, model_size, language)

        Returns:
            Tuple[str, Optional[str], Optional[Exception]]:
                (file_path, transcription or None, exception or None)
        """
        file_path, model_size, language = args
        try:
            # Transcribe without printing status (will be handled by progress reporting)
            transcription = self.transcription_service.transcribe_audio(
                file_path, model_size, language
            )
            return file_path, transcription, None
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            return file_path, None, e

    def process_files_parallel(
        self,
        input_dir: str,
        output_dir: Optional[str] = None,
        num_processes: Optional[int] = None,
        model_size: Optional[str] = None,
        language: Optional[str] = None,
    ) -> List[str]:
        """Process multiple audio files in parallel using multiprocessing.

        Args:
            input_dir: Directory containing audio files to process
            output_dir: Directory to save processed output (uses AUDIO_OUTPUT_DIR env var if None)
            num_processes: Number of parallel processes to use (defaults to CPU count)
            model_size: Whisper model size (tiny, base, small, medium, large)
            language: Language code to use (e.g., 'en' for English)

        Returns:
            List[str]: List of successful transcriptions

        Raises:
            FileOperationError: If directory operations fail
        """
        # Set output directory in environment for transcription service to use
        if output_dir:
            os.environ["AUDIO_OUTPUT_DIR"] = output_dir

        # Use default number of processes if not specified
        if num_processes is None:
            num_processes = max(1, multiprocessing.cpu_count() - 1)

        # Validate input directory
        if not os.path.isdir(input_dir):
            raise FileOperationError(f"Input directory not found: {input_dir}")

        # Find all audio files in the directory
        audio_files = [
            os.path.join(input_dir, f)
            for f in os.listdir(input_dir)
            if f.lower().endswith((".wav", ".mp3", ".flac", ".ogg"))
        ]

        if not audio_files:
            logger.warning(f"No audio files found in {input_dir}")
            print(
                f"{Fore.YELLOW}No audio files found in {input_dir}{Style.RESET_ALL}"
            )
            return []

        logger.info(f"Found {len(audio_files)} audio files to process")
        print(
            f"{Fore.CYAN}Processing {len(audio_files)} audio files with {num_processes} processes...{Style.RESET_ALL}"
        )

        # Create process pool
        successful_transcriptions = []
        failed_files = []

        try:
            # Create a pool of worker processes
            pool = multiprocessing.Pool(processes=num_processes)

            # Prepare arguments for each file
            process_args = [
                (file_path, model_size, language) for file_path in audio_files
            ]

            # Apply the processing function asynchronously
            results = []
            for args in process_args:
                r = pool.apply_async(self._process_file, (args,))
                results.append(r)

            # Initialize progress bar
            with tqdm(
                total=len(results), desc="Processing audio files"
            ) as pbar:
                # Process results as they complete
                for r in results:
                    try:
                        file_path, transcription, error = r.get()
                        if error:
                            failed_files.append((file_path, str(error)))
                            print(
                                f"{Fore.RED}Error processing {file_path}: {error}{Style.RESET_ALL}"
                            )
                        else:
                            successful_transcriptions.append(transcription)
                        pbar.update(1)
                    except Exception as e:
                        logger.error(f"Error retrieving result: {e}")
                        print(
                            f"{Fore.RED}Error retrieving result: {e}{Style.RESET_ALL}"
                        )
                        pbar.update(1)

            # Clean up
            pool.close()
            pool.join()

        except Exception as e:
            logger.error(f"Error in parallel processing: {e}")
            print(
                f"{Fore.RED}Error in parallel processing: {e}{Style.RESET_ALL}"
            )
            # Try to clean up if possible
            try:
                pool.terminate()
                pool.join()
            except:
                pass

        # Report results
        print(
            f"{Fore.GREEN}Successfully processed {len(successful_transcriptions)} files{Style.RESET_ALL}"
        )
        if failed_files:
            print(
                f"{Fore.YELLOW}Failed to process {len(failed_files)} files{Style.RESET_ALL}"
            )
            for file_path, error in failed_files:
                print(f"{Fore.RED}- {file_path}: {error}{Style.RESET_ALL}")

        print(f"{Fore.CYAN}Finished processing all files{Style.RESET_ALL}")
        return successful_transcriptions

    def transcribe_directory(
        self,
        directory: Optional[str] = None,
        model_size: Optional[str] = None,
        language: Optional[str] = None,
        parallel: bool = False,
        num_processes: Optional[int] = None,
    ) -> List[str]:
        """Transcribe all WAV files in a directory.

        Args:
            directory: Directory containing WAV files (defaults to AUDIO_INPUT_DIR)
            model_size: Whisper model size (tiny, base, small, medium, large)
            language: Language code to use (e.g., 'en' for English).
                If provided, skips language detection.
            parallel: Whether to use parallel processing
            num_processes: Number of parallel processes to use (defaults to CPU count)

        Returns:
            List[str]: List of paths to transcription files

        Raises:
            FileOperationError: If directory operations fail
        """
        # Use provided directory or get from environment
        if not directory:
            directory = os.environ.get("AUDIO_INPUT_DIR", "input")

        # Validate directory
        if not os.path.isdir(directory):
            raise FileOperationError(f"Directory not found: {directory}")

        # If parallel processing is requested, use the parallel implementation
        if parallel:
            return self.process_files_parallel(
                directory,
                None,  # Use default output directory
                num_processes,
                model_size,
                language,
            )

        # Find all WAV files in the directory
        wav_files = [
            os.path.join(directory, f)
            for f in os.listdir(directory)
            if f.lower().endswith(".wav")
        ]

        if not wav_files:
            print(
                f"{Fore.YELLOW}No WAV files found in {directory}{Style.RESET_ALL}"
            )
            return []

        # Transcribe each file
        transcriptions = []
        for wav_file in wav_files:
            try:
                transcription = self.transcribe_file(
                    wav_file, model_size, language
                )
                transcriptions.append(transcription)
            except Exception as e:
                logger.error(f"Error transcribing {wav_file}: {e}")
                print(
                    f"{Fore.RED}Error transcribing {wav_file}: {e}{Style.RESET_ALL}"
                )

        return transcriptions
