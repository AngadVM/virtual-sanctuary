from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import concurrent.futures
import asyncio
import os

from Modules.news import get_news_rss
from Modules.animals import API_Response
from Modules.animal_viz import create_visualization

app = Flask(__name__)
CORS(app)

# Thread pool for CPU-bound tasks
executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)


def stream_species_data(species_data):
    """Generator function to stream species JSON one by one, including audio and news."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    for species_name, data in species_data.items():
        try:
            
            # Fetch news articles
            news_articles = get_news_rss(species_name)
            data['news'] = news_articles

            # Convert to JSON and stream in formatted manner
            json_data = json.dumps({species_name: data}, indent=4)
            
            yield f"data: {json_data}\n\n"

        except Exception as e:
            print(f"Error streaming data for {species_name}: {str(e)}")
            error_data = json.dumps({'error': f"Error processing {species_name}: {str(e)}"}, indent=4)
            yield f"data: {error_data}\n\n"

@app.route("/explore", methods=["POST"]) 
def explore():
    """Handles species retrieval based on location and returns JSON response."""
    location = request.json.get('location')
    
    if not location:
        return jsonify({"error": "Location not provided"}), 400
    
    try:
        result = asyncio.run(API_Response(location))  # Fetch species data
        
        if "error" in result:
            return jsonify(result), 404

        # Process each species data
        processed_data = {}
        for species_name, data in result["species_data"].items():
            try:
                

                # Fetch news articles
                news_articles = get_news_rss(species_name)
                data['news'] = news_articles

                processed_data[species_name] = data

            except Exception as e:
                print(f"Error processing data for {species_name}: {str(e)}")
                processed_data[species_name] = {
                    "error": f"Error processing {species_name}: {str(e)}"
                }

        return jsonify({
            "success": True,
            "data": processed_data,
        })

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



@app.route("/api/health")
def health_check():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(debug=True, threaded=True)
