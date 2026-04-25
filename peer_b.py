import asyncio
import requests

from aiortc import RTCPeerConnection, RTCSessionDescription
from audio_track import MicrophoneAudioTrack
from audio_output import play_audio
from const import *

try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

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

@pc.on("icecandidate")
def on_icecandidate(candidate):
    if candidate:
        import requests
        requests.post("http://"+SIGNALING_SERVER+":8080/candidate/b", data=candidate.to_sdp())

@pc.on("connectionstatechange")
async def on_state_change():
    print("Connection state:", pc.connectionState)

async def receive_candidates():
    import requests
    seen = set()

    while True:
        r = requests.get("http://"+SIGNALING_SERVER+":8080/candidate/a")
        for c in r.json():
            if c not in seen:
                seen.add(c)
                from aiortc import RTCIceCandidate
                candidate = RTCIceCandidate.sdpParse(c)
                await pc.addIceCandidate(candidate)
        await asyncio.sleep(1)

async def run():
    print("Waiting for offer...")
    asyncio.create_task(receive_candidates())
    
    while True:
        r = requests.get("http://"+SIGNALING_SERVER+":8080/offer")
        if r.text:
            break
        await asyncio.sleep(1)

    await pc.setRemoteDescription(
        RTCSessionDescription(sdp=r.text, type="offer")
    )

    print("Senders:", pc.getSenders())
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    requests.post("http://"+SIGNALING_SERVER+":8080/answer", data=answer.sdp)

    print("Connected!")

    while True:
        await asyncio.sleep(1)

asyncio.run(run())
