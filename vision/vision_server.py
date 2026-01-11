from flask import Flask, jsonify
from vision import vision_state, vision_lock
import time

app = Flask(__name__)

@app.route("/vision", methods=["GET"])
def vision():
    with vision_lock:
        return jsonify(vision_state)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9100)
