from flask import Flask, jsonify

def create_server(state, lock):
    app = Flask(__name__)

    @app.route("/vision", methods=["GET"])
    def vision():
        with lock:
            return jsonify(state)

    return app
