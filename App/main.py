from functools import lru_cache
from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
import json
import concurrent.futures
import time
import asyncio
import aiohttp
import tempfile
import uuid
import shutil
import os

from Modules.llm import narrate
from Modules.news import get_news_rss
from Modules.aud import process_audio
from Modules.animals import API_Response
from Modules.animal_viz import create_visualization

app = Flask(__name__)
CORS(app)

# Thread pool for CPU-bound tasks
executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)

@lru_cache(maxsize=100)
def get_cached_narrative(species_name):
    """Fetch and cache the narrative for a species"""
    return narrate(species_name)

def stream_species_data(species_data):
    """Generator function to stream species JSON one by one, including audio and news."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    for species_name, data in species_data.items():
        try:
            # Generate and cache narrative
            narrative = get_cached_narrative(species_name)
            data['narrative'] = narrative

            # Process audio asynchronously
            audio_files = data.get('audio', [])
            
            # Process audio and ensure we get a valid output filename
            output_filename = loop.run_until_complete(process_audio(narrative, audio_files))
            
            if output_filename:
                # Make sure the path is properly formatted for the frontend
                audio_path = f"/audio/{output_filename}"
                data['audio_path'] = audio_path
                print(f"Added audio path: {audio_path} for species: {species_name}")
            else:
                # Log the error and include an empty path
                print(f"Failed to generate audio for {species_name}")
                data['audio_path'] = ""

            # Fetch news articles
            news_articles = get_news_rss(species_name)
            data['news'] = news_articles

            # Convert to JSON and stream in formatted manner
            json_data = json.dumps({species_name: data}, indent=4)
            
            # Debug: Check if audio_path is in the JSON data
            if 'audio_path' not in data:
                print(f"Warning: audio_path is missing for {species_name}")
            
            yield f"data: {json_data}\n\n"
            time.sleep(0.5)  # Reduced delay for faster streaming

        except Exception as e:
            print(f"Error streaming data for {species_name}: {str(e)}")
            error_data = json.dumps({'error': f"Error processing {species_name}: {str(e)}"}, indent=4)
            yield f"data: {error_data}\n\n"

@app.route("/explore", methods=["POST"]) 
def explore():
    """Handles species retrieval based on location and streams the response."""
    location = request.json.get('location')
    
    if not location:
        return jsonify({"error": "Location not provided"}), 400
    
    try:
        start_time = time.time()
        result = asyncio.run(API_Response(location))  # Fetch species data
        api_time = time.time() - start_time
        print(f"API Response time: {api_time:.2f} seconds")
        
        if "error" in result:
            return jsonify(result), 404

        return Response(stream_species_data(result["species_data"]), mimetype="text/event-stream")

    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route("/visualize", methods=["POST"])
def visualize():
    """Handles species visualization requests."""
    if request.method == "POST":
        animal_name = request.json.get('animal')
        
        if not animal_name:
            return jsonify({"error": "Animal name not provided"}), 400
        
        try:
            file_path = create_visualization(animal_name)
            
            if not file_path:
                return jsonify({"error": "No data found for the specified animal"}), 404
            
            return jsonify({
                "success": True,
                "file_path": file_path,
                "message": "Visualization created successfully"
            })

        except Exception as e:
            error_msg = {'error': f'An error occurred: {str(e)}'}
            print("Visualization Error:", error_msg)
            return jsonify(error_msg), 500

@app.route("/audio/<filename>")
def serve_audio(filename):
    """Serve audio files with improved error handling."""
    audio_dir = "./Temp/Mixed"
    
    # Verify the file exists
    file_path = os.path.join(audio_dir, filename)
    if not os.path.isfile(file_path):
        print(f"Audio file not found: {file_path}")
        return jsonify({"error": "Audio file not found"}), 404
    
    # Log successful audio requests
    print(f"Serving audio file: {filename}")
    return send_from_directory(audio_dir, filename)

@app.route("/api/health")
def health_check():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(debug=True, threaded=True)
