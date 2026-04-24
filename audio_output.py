import sounddevice as sd
import numpy as np

def play_audio(frame):
    pcm = frame.to_ndarray()
    audio = pcm.astype(np.float32) / 32768.0
    sd.play(audio, samplerate=48000, blocking=False)
