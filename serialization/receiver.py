from flask import Flask, request

app = Flask(__name__)

@app.route("/robot", methods=["POST"])
def robot():
    data = request.get_json(force=True, silent=True)
    print("RECEIVED:", data, flush=True)
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000, debug=False)
