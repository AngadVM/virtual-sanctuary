import asyncio
import edge_tts

VOICE = 'en-CA-LiamNeural'  
OUTPUT_FILE = "./Temp/Normal/main.mp3"

async def generate_speech(text):
    communicate = edge_tts.Communicate(text, VOICE, rate="-15%", pitch="-5Hz", volume="+20%")
    await communicate.save(OUTPUT_FILE)

def speak(text):
    asyncio.run(generate_speech(text))

if __name__ == "__main__":
    speak(input("> "))
