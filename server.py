from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

@app.route('/')
def home():
    return "Holehe API running"

@app.route('/holehe')
def holehe_lookup():
    email = request.args.get("email")
    if not email:
        return jsonify({"error": "Missing email parameter"}), 400

    try:
       
        result = subprocess.run(
            ["python", "-m", "holehe", email, "--no-color"],
            capture_output=True,
            text=True,
            timeout=60
        )
        output = result.stdout.strip()
        if not output:
            return jsonify({"error": "No output"}), 500
        return jsonify({"output": output})
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Holehe timed out"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
