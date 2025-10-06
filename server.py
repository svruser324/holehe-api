from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({"status": "Holehe API is running ✅"})

@app.route("/holehe")
def holehe_lookup():
    email = request.args.get("email")
    if not email:
        return jsonify({"error": "Please provide ?email=someone@example.com"}), 400

    try:
        result = subprocess.run(
            ["holehe", email, "--no-color"],
            capture_output=True,
            text=True,
            timeout=60
        )
        output = result.stdout.strip() or result.stderr.strip() or "No output"
        return jsonify({"output": output})
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Holehe scan timed out"}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
