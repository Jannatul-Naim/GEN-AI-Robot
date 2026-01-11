from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/robot", methods=["POST"])
def robot():
    data = request.get_json()
    print("Received JSON:")
    print(data)
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000)
