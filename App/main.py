from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import concurrent.futures
import asyncio
import os

from Modules.news import get_news_rss
from Modules.animals import API_Response
from Modules.animal_viz import create_visualization

# Change the static_folder to point to the correct directory
app = Flask(__name__, static_folder='../visualizations')
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

@app.route('/visualize', methods=['POST'])
def visualize_animal():
    try:
        data = request.json
        animal_name = data.get('animal')
        
        if not animal_name:
            return jsonify({'success': False, 'error': 'Animal name is required'})
            
        # Call the create_visualization function from animal_viz.py
        # Now it returns just the filename, not the full path
        filename = create_visualization(animal_name)
        
        if not filename:
            return jsonify({'success': False, 'error': 'Failed to create visualization'})
            
        # Return the full URL that the frontend can access
        # This includes the protocol, hostname, and port
        file_url = f"http://localhost:5000/visualizations/{filename}"
        
        return jsonify({
            'success': True, 
            'file_path': file_url,
            'filename': filename
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/visualizations/<path:filename>')
def serve_visualization(filename):
    # Serve files from the visualizations directory
    print(f"Serving visualization file: {filename}")
    return send_from_directory('../visualizations', filename)

@app.route("/api/health")
def health_check():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(debug=True, threaded=True)