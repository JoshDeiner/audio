import sounddevice as sd
from scipy.io.wavfile import write
import time
from colorama import Fore, Style, init

# Initialize colorama
init()

duration = 5  # seconds to record
sample_rate = 44100

# Countdown before recording
print(f"{Fore.CYAN}Recording countdown.{Style.RESET_ALL}")
print()
print(f"{Fore.YELLOW}Recording will start in:{Style.RESET_ALL}")
for i in range(3, 0, -1):
    color = Fore.RED if i == 1 else (Fore.YELLOW if i == 2 else Fore.GREEN)
    print(f"  {color}{i}...{Style.RESET_ALL}")
    time.sleep(1)

print("Recording now...")
recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=2, dtype='int16')
sd.wait()
print("Recording complete.")

write("recorded.wav", sample_rate, recording)
print("Saved as 'recorded.wav'")

