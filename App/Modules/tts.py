import asyncio
import edge_tts


TEXT = "Hello! Don't forget to like the video if you find it helpful, thank you"
VOICE = 'en-CA-LiamNeural'  
OUTPUT_FILE = "test.mp3"

async def amain() -> None:
    communicate = edge_tts.Communicate(TEXT, VOICE)
    await communicate.save(OUTPUT_FILE)

loop = asyncio.get_event_loop_policy().get_event_loop()
try:
    loop.run_until_complete(amain())
finally:
    loop.close()
