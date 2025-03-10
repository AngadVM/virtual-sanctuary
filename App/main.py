from Modules.llm import narrate
from Modules.news import get_news_rss
from Modules.aud import combine
from Modules.animals import API_Response
from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio


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
                print("Backend Error Response:", result)  # Log error
                return jsonify(result), 404
            
            print("Backend Success Response:", result)  # Log response
            return jsonify(result)

        except Exception as e:
            error_msg = {'error': f'An error occurred: {str(e)}'}
            print("Backend Exception:", error_msg)  # Log error
            return jsonify(error_msg), 500


if __name__ == "__main__":
    app.run(debug=True)