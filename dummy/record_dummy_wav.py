import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np


def record_wav(filename="dummy_speech.wav", duration=5, samplerate=16000):
    print(f"Recording for {duration} seconds...")

    audio = sd.rec(
        int(duration * samplerate),
        samplerate=samplerate,
        channels=1,
        dtype="int16",
    )
    sd.wait()  # Wait until recording is finished

    write(filename, samplerate, audio)
    print(f"Recording saved to: {filename}")


if __name__ == "__main__":
    record_wav()
