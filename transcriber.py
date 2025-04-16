#!/usr/bin/env python3
import os
import wave
import pyaudio
import logging
import time
from colorama import Fore, Style, init

# Initialize colorama
init()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def record_audio(duration=5, rate=44100, chunk=1024, channels=1, format_type=pyaudio.paInt16):
    """
    Record audio from microphone and save to a WAV file.
    
    Args:
        duration (int): Recording duration in seconds
        rate (int): Sample rate in Hz (16kHz for Whisper)
        chunk (int): Buffer size
        channels (int): Number of audio channels (1 for mono)
        format_type: Audio format (from pyaudio constants)
        
    Returns:
        str: Path to the saved WAV file
    """
    # Get the input directory from environment variable
    input_dir = os.environ.get("AUDIO_INPUT_DIR")
    if not input_dir:
        raise ValueError("AUDIO_INPUT_DIR environment variable must be set")
    
    # Check if directory exists
    if not os.path.isdir(input_dir):
        raise FileNotFoundError(f"Input directory does not exist: {input_dir}")
    
    # Define output file path
    output_path = os.path.join(input_dir, "voice.wav")
    
    # Initialize PyAudio
    audio = pyaudio.PyAudio()
    
    # Countdown before recording
    print('\n')
    print(f"{Fore.CYAN}Recording countdown.{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Recording will start in:{Style.RESET_ALL}")
    print('\n')
    for i in range(3, -1, -1):
        if i == 0:
            print(f"{Fore.MAGENTA}  {i}...{Style.RESET_ALL}")
        elif i == 1:
            print(f"{Fore.RED}  {i}...{Style.RESET_ALL}")
        elif i == 2:
            print(f"{Fore.YELLOW}  {i}...{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}  {i}...{Style.RESET_ALL}")
        time.sleep(1)
    print(f"{Fore.CYAN}Recording now! {Fore.GREEN}Speak clearly...{Style.RESET_ALL}")
    print('\n')
    
    # Open audio stream for recording
    logger.info("Recording started...")
    
    stream = audio.open(
        format=format_type,
        channels=channels,
        rate=rate,
        input=True,
        frames_per_buffer=chunk
    )
    
    # Record audio data
    frames = []
    total_iterations = int(rate / chunk * duration)
    
    for i in range(0, total_iterations):
        data = stream.read(chunk)
        frames.append(data)
        # Show progress during recording
        if i % int(rate / chunk) == 0:  # Approximately every second
            seconds_left = duration - (i // int(rate / chunk))
            print(f"{Fore.BLUE}Recording: {Fore.GREEN}{seconds_left}{Fore.BLUE} seconds left...{Style.RESET_ALL}")
    
    # Ensure we display zero seconds at the end
    print(f"{Fore.BLUE}Recording: {Fore.GREEN}0{Fore.BLUE} seconds left...{Style.RESET_ALL}")
    
    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    audio.terminate()
    
    print('\n')
    logger.info("Recording finished.")
    
    # Save to WAV file
    with wave.open(output_path, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(audio.get_sample_size(format_type))
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))
    
    logger.info(f"Saved to {output_path}")
    return output_path

def main():
    """Entry point when script is run directly."""
    output_path = record_audio()
    logger.info(f"Audio recording complete. Saved to {output_path}")
    return output_path

if __name__ == "__main__":
    main()
