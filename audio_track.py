import numpy as np
import sounddevice as sd
from aiortc import MediaStreamTrack
import av
import asyncio

class MicrophoneAudioTrack(MediaStreamTrack):
    kind = "audio"

    def __init__(self):
        super().__init__()
        self.sample_rate = 48000
        self.samples_per_frame = 960  # 20 ms
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype="int16",
            blocksize=self.samples_per_frame
        )
        self.stream.start()

    async def recv(self):
        pts, time_base = await self.next_timestamp()

        audio, _ = self.stream.read(self.samples_per_frame)

        frame = av.AudioFrame.from_ndarray(audio, layout="mono")
        frame.sample_rate = self.sample_rate
        frame.pts = pts
        frame.time_base = time_base

        return frame
