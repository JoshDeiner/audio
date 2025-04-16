#!/usr/bin/env python3
"""
Simple app that records from a file or device without Docker
"""
import os
import wave
import pyaudio
import logging
import sys
import time
from colorama import Fore, Style, init

# Initialize colorama
init()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def list_audio_devices():
    """List all available audio devices"""
    audio = pyaudio.PyAudio()
    info = "\nAvailable audio devices:\n"
    
    for i in range(audio.get_device_count()):
        try:
            dev_info = audio.get_device_info_by_index(i)
            name = dev_info['name']
            channels = dev_info['maxInputChannels']
            if channels > 0:
                info += f"{Fore.GREEN}[{i}] {name} (Input Channels: {channels}){Style.RESET_ALL}\n"
            else:
                info += f"[{i}] {name} (Output only)\n"
        except Exception as e:
            info += f"[{i}] Could not get device info: {str(e)}\n"
    
    audio.terminate()
    return info

def record_audio(device_index=None, duration=5, rate=44100):
    """
    Record audio from the specified device
    
    Args:
        device_index: Device index to use (None for default)
        duration: Recording duration in seconds
        rate: Sample rate
    """
    # Ensure we have an output directory
    os.makedirs("input", exist_ok=True)
    output_path = os.path.join("input", "voice.wav")
    
    audio = pyaudio.PyAudio()
    chunk = 1024
    
    # Show device info
    if device_index is not None:
        try:
            device_info = audio.get_device_info_by_index(device_index)
            print(f"Using device: {device_info['name']}")
        except:
            print(f"Invalid device index: {device_index}")
            return None
    
    # Countdown
    print(f"{Fore.CYAN}Recording will start in:{Style.RESET_ALL}")
    for i in range(3, 0, -1):
        print(f"{Fore.YELLOW}  {i}...{Style.RESET_ALL}")
        time.sleep(1)
    
    print(f"{Fore.GREEN}Recording now!{Style.RESET_ALL}")
    
    # Open stream
    try:
        stream = audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=rate,
            input=True,
            input_device_index=device_index,
            frames_per_buffer=chunk
        )
    except Exception as e:
        logger.error(f"Error opening stream: {e}")
        audio.terminate()
        return None
    
    # Record
    frames = []
    for i in range(0, int(rate / chunk * duration)):
        try:
            data = stream.read(chunk, exception_on_overflow=False)
            frames.append(data)
            if i % int(rate / chunk) == 0:
                seconds_left = duration - (i // int(rate / chunk))
                print(f"{Fore.BLUE}Recording: {seconds_left} seconds left{Style.RESET_ALL}")
        except Exception as e:
            logger.error(f"Error recording: {e}")
            break
    
    # Clean up
    stream.stop_stream()
    stream.close()
    
    # Save recording
    with wave.open(output_path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))
    
    audio.terminate()
    logger.info(f"Recording saved to {output_path}")
    return output_path

def main():
    """Main application entry point"""
    print(f"{Fore.CYAN}=== Simple Audio Recorder ==={Style.RESET_ALL}")
    
    # List available devices
    print(list_audio_devices())
    
    # Ask for device selection
    try:
        device_str = input(f"{Fore.YELLOW}Enter device index to use (or press Enter for default): {Style.RESET_ALL}")
        device_index = int(device_str) if device_str.strip() else None
    except ValueError:
        device_index = None
    
    # Record audio
    output_path = record_audio(device_index)
    
    if output_path:
        print(f"{Fore.GREEN}Recording completed successfully! File saved to: {output_path}{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}Recording failed.{Style.RESET_ALL}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())