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
        print("Receiving audio from Peer B")

        async def recv_audio():
            while True:
                frame = await track.recv()
                play_audio(frame)

        asyncio.create_task(recv_audio())


async def run():
    offer = await pc.createOffer()
    await pc.setLocalDescription(offer)

    requests.post("http://localhost:8080/offer", data=offer.sdp)

    print("Waiting for answer...")

    while True:
        r = requests.get("http://localhost:8080/answer")
        if r.text:
            break
        await asyncio.sleep(1)

    await pc.setRemoteDescription(
        RTCSessionDescription(sdp=r.text, type="answer")
    )

    print("Connected!")

    while True:
        await asyncio.sleep(1)


asyncio.run(run())
