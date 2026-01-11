from flask import Flask, jsonify
from vision.vision import vision_state, vision_lock

app = Flask(__name__)

@app.route("/vision", methods=["GET"])
def vision():
    with vision_lock:
        return jsonify(vision_state)

