import google.generativeai as genai
from dotenv import load_dotenv
import os


load_dotenv()
genai.configure(api_key=os.getenv('API'))

def generate_narration(timestamp_data: list) -> str:
    """Generate timestamped narration from admin's input using Gemini."""
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    prompt = """Act as David Attenborough. Create a VR video narration using these timestamped events. 
    Format each entry exactly as [HH:MM:SS] followed by the description. Note: Do not disclose any location and only describe the timestamped events. Events:
    """
    for ts, desc in timestamp_data:
        prompt += f"\n- {ts} - {desc}"
    
    response = model.generate_content(prompt + "\nNarration:")
    return response.text
