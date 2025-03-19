import google.generativeai as genai
from dotenv import load_dotenv
import os
from time import time


load_dotenv()
api_key = os.environ.get('API')
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")


def narrate(name: str) -> str:

    response = model.generate_content(f"Acting as David Attenborough, narrate the life of {name} without any markdown formatting. Do not mention where the specie stays or is found.")

    return response.text


if __name__ == "__main__":

    start = time()

    print(narrate("Red Panda"))

    end = time()

    print(end - start)