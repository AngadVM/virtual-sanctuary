from Modules.llm import narrate
from Modules.news import get_news_rss
from Modules.aud import combine
from Modules.animals import API_Response
from flask import Flask, request, jsonify, send_from_directory
from Modules.tts import speak
from flask_cors import CORS
import asyncio
import os
import requests


app = Flask(__name__)
CORS(app)


@app.route("/explore", methods=["POST", "GET"]) 
def index():
    if request.method == "POST":
        location = request.json.get('location')
        
        if not location:
            return jsonify({"error": "Location not provided"}), 400
        
        try:
            result = asyncio.run(API_Response(location))
            
            if "error" in result:
                print("Backend Error Response:", result)
                return jsonify(result), 404
            
            # Process narratives for each species
            for species_name, data in result['species_data'].items():
                # Generate narrative using LLM
                narrative = narrate(species_name)
                data['narrative'] = narrative
                
                # We'll handle audio generation in a separate endpoint
                
            print("Backend Success Response:", result)
            return jsonify(result)

        except Exception as e:
            error_msg = {'error': f'An error occurred: {str(e)}'}
            print("Backend Exception:", error_msg)
            return jsonify(error_msg), 500

@app.route("/generate-audio", methods=["POST"])
def generate_audio():
    try:
        species = request.json.get('species')
        narrative = request.json.get('narrative')
        
        if not species or not narrative:
            return jsonify({"error": "Species name or narrative missing"}), 400
        
        # Create directories if they don't exist
        os.makedirs("./Temp/Normal", exist_ok=True)
        os.makedirs("./Temp/Mixed", exist_ok=True)
        os.makedirs("./Temp/Background", exist_ok=True)
        
        # Generate TTS for the narrative
        speak(narrative)
        
        # Mix with animal sounds (if available)
        audio_files = request.json.get('audio_files', [])
        if audio_files:
            # Download the first audio file from Xeno-canto
            audio_url = audio_files[0].get('url')
            # You'll need to implement a function to download the audio file
            download_audio(audio_url, "./Temp/Background/animal.mp3")
            
        # Combine audio
        combine()
        
        # Return the path or serve the file
        return jsonify({"audio_path": "/audio/mixed_output.mp3"})
        
    except Exception as e:
        return jsonify({"error": f"Audio generation failed: {str(e)}"}), 500

@app.route("/audio/<filename>")
def serve_audio(filename):
    return send_from_directory("./Temp/Mixed", filename)


def download_audio(url, save_path):
    """
    Download audio file from a URL and save it.
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error downloading audio: {e}")
        return False


if __name__ == "__main__":

    app.run(debug=True)