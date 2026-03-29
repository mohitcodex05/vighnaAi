import asyncio
from livekit.rtc import Room
from config import LIVEKIT_URL, TOKEN

async def connect_room():
    room = Room()
    await room.connect(LIVEKIT_URL, TOKEN)
    print("✅ Connected to LiveKit")
    return room
