from flask import Flask, request, jsonify
import subprocess
import json

app = Flask(__name__)

@app.route("/")
def home():
    return "Holehe API running"

@app.route("/holehe", methods=["GET"])
def holehe_lookup():
    email = request.args.get("email")
    if not email:
        return jsonify({"error": "Missing email"}), 400

    try:
        # Run holehe command (only used sites, JSON output)
        result = subprocess.run(
            ["holehe", "--only-used", "--json", email],
            capture_output=True,
            text=True,
            timeout=60
        )

        output = result.stdout.strip()
        if not output:
            return jsonify({"error": "No output"}), 500

        try:
            data = json.loads(output)
        except json.JSONDecodeError:
            data = {"raw_output": output}

        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
