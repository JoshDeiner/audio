import sounddevice as sd
from scipy.io.wavfile import write
import time

duration = 5  # seconds to record
sample_rate = 44100

# Countdown before recording
print("Get ready! Recording starts in:")
for i in range(3, 0, -1):
    print(i)
    time.sleep(1)

print("Recording now...")
recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=2, dtype='int16')
sd.wait()
print("Recording complete.")

write("recorded.wav", sample_rate, recording)
print("Saved as 'recorded.wav'")

