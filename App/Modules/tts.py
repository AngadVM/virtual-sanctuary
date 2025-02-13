import asyncio
import edge_tts

VOICE = 'en-CA-LiamNeural'  
OUTPUT_FILE = "./Temp/Normal/main.mp3"

def speak(text):

    async def amain() -> None:
        communicate = edge_tts.Communicate(text, VOICE, rate="-15%", pitch="-5Hz", volume="+20%")
        await communicate.save(OUTPUT_FILE)

    loop = asyncio.get_event_loop_policy().get_event_loop()
    try:
        loop.run_until_complete(amain())
    finally:
        loop.close()

if __name__ == "__main__":

    speak(input("> "))