import asyncio
import requests

from aiortc import RTCPeerConnection, RTCSessionDescription
from audio_track import MicrophoneAudioTrack
from audio_output import play_audio

pc = RTCPeerConnection()

# Send mic audio
pc.addTrack(MicrophoneAudioTrack())

@pc.on("track")
def on_track(track):
    if track.kind == "audio":
        print("Receiving audio from Peer A")

        async def recv_audio():
            while True:
                frame = await track.recv()
                play_audio(frame)

        asyncio.create_task(recv_audio())


async def run():
    print("Waiting for offer...")

    while True:
        r = requests.get("http://localhost:8080/offer")
        if r.text:
            break
        await asyncio.sleep(1)

    await pc.setRemoteDescription(
        RTCSessionDescription(sdp=r.text, type="offer")
    )

    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    requests.post("http://localhost:8080/answer", data=answer.sdp)

    print("Connected!")

    while True:
        await asyncio.sleep(1)


asyncio.run(run())
