import cmd
from flask import Flask, request

import angles

app = Flask(__name__)

@app.route("/robot", methods=["POST"])
def robot():
    data = request.get_json(force=True, silent=True)
    print("RECEIVED:", data, flush=True)
    return "OK", 200

