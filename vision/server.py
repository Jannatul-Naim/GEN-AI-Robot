from flask import Flask, jsonify

def create_server(state, lock):
    app = Flask(__name__)

    @app.route("/vision", methods=["GET"])
    def vision():
        with lock:
            cleaned_objects = [
                {
                    "name": obj["name"],
                    "x_cm": obj["x_cm"],
                    "z_cm": obj["z_cm"]
            }
            for obj in state["objects"]
        ]

        return jsonify({
        "objects": cleaned_objects
    })


    return app
