from flask import Flask, jsonify, send_file, request, abort
import os
import json
import flask_cors
from interface import process_request

app = Flask(__name__)
flask_cors.CORS(app)

@app.route('/health-check', methods=['GET'])
def health_check():
    return {"status": "ok for population"}, 200

@app.route('/populate', methods=['POST'])
def populate():
    json = request.get_json(force=True)
    data = process_request(json)
    return jsonify(str(data))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
