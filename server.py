from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Holehe API is running"

@app.route('/holehe')
def holehe_lookup():
    email = request.args.get("email")
    if not email:
        return jsonify({"error": "Missing email parameter"}), 400

    try:
        # run holhe
        result = subprocess.run(
            ["python3", "-m", "holehe", email, "--no-color"],
            capture_output=True,
            text=True,
            timeout=60
        )

        
        output = (result.stdout + "\n" + result.stderr).strip()

        if not output:
            return jsonify({"error": "No output from holehe"}), 500

        
        return jsonify({"output": output})

    except subprocess.TimeoutExpired:
        return jsonify({"error": "Holehe timed out"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
