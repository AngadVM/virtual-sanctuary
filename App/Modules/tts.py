import asyncio
import edge_tts
import os

VOICE = 'en-CA-LiamNeural'  
OUTPUT_FILE = "./Temp/Normal/main.mp3"

async def generate_speech(text, output_file=OUTPUT_FILE):
    """Generate speech from text and save to file"""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    communicate = edge_tts.Communicate(text, VOICE, rate="-15%", pitch="-5Hz", volume="+20%")
    await communicate.save(output_file)
    return output_file

async def speak(text, output_file=OUTPUT_FILE):
    """Wrapper for generate_speech to be used with asyncio"""
    return await generate_speech(text, output_file)

def speak_sync(text, output_file=OUTPUT_FILE):
    """Synchronous wrapper for speak"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(speak(text, output_file))
    finally:
        loop.close()

if __name__ == "__main__":
    speak_sync(input("> "))