import asyncio
import aiohttp
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
        print("Receiving audio from Peer B")

        async def recv_audio():
            while True:
                frame = await track.recv()
                play_audio(frame)

        loop = asyncio.get_running_loop()
        loop.create_task(recv_audio())
        #asyncio.create_task(recv_audio())

@pc.on("icecandidate")
def on_icecandidate(candidate):
    if candidate:
        print("Generated candidate:", candidate.candidate)
        #requests.post(
        #    "http://"+SIGNALING_SERVER+":8080/candidate/a",
        #    json={
        #        "candidate": candidate.candidate,
        #        "sdpMid": candidate.sdpMid,
        #        "sdpMLineIndex": candidate.sdpMLineIndex,
        #    },
        #)
        async with aiohttp.ClientSession() as session:
            await session.post("http://"+SIGNALING_SERVER+":8080/candidate/a", json={
                    "candidate": candidate.candidate,
                    "sdpMid": candidate.sdpMid,
                    "sdpMLineIndex": candidate.sdpMLineIndex,
                }
            )

@pc.on("connectionstatechange")
async def on_state_change():
    print("Connection state:", pc.connectionState)

@pc.on("iceconnectionstatechange")
async def on_ice_state():
    print("ICE state:", pc.iceConnectionState)

async def receive_candidates():
    import requests
    from aiortc import RTCIceCandidate

    seen = set()

    while True:
        #r = requests.get("http://"+SIGNALING_SERVER+":8080/candidate/b")
        async with aiohttp.ClientSession() as session:
            async with session.get("http://"+SIGNALING_SERVER+":8080/candidate/b") as resp:
                rjson = await resp.json()
        for c in rjson:
            key = str(c)
            if key not in seen:
                seen.add(key)

                candidate = RTCIceCandidate(
                    candidate=c["candidate"],
                    sdpMid=c["sdpMid"],
                    sdpMLineIndex=c["sdpMLineIndex"],
                )

                await pc.addIceCandidate(candidate)

        await asyncio.sleep(0.5)

async def run():
    print("Senders:", pc.getSenders())
    
    asyncio.create_task(receive_candidates())
    offer = await pc.createOffer()
    await pc.setLocalDescription(offer)
    # WAIT for ICE gathering to finish
    while pc.iceGatheringState != "complete":
        await asyncio.sleep(0.1)

    # WAIT for ICE gathering
    while pc.iceGatheringState != "complete":
        await asyncio.sleep(0.1)

    #requests.post("http://"+SIGNALING_SERVER+":8080/offer", data=offer.sdp)
    async with aiohttp.ClientSession() as session:
        await session.post("http://"+SIGNALING_SERVER+":8080/offer", data=offer.sdp)

    print("Waiting for answer...")

    while True:
        #r = requests.get("http://"+SIGNALING_SERVER+":8080/answer")
        async with aiohttp.ClientSession() as session:
            async with session.get("http://"+SIGNALING_SERVER+":8080/candidate/b") as resp:
                r = await resp
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
