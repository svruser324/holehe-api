from flask import Flask, request, jsonify, make_response
import subprocess, re, os, requests

app = Flask(__name__)
ALLOWED_ORIGIN = "*"  
MAX_OUTPUT_CHARS = 20000
RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY", "")  

def strip_ansi(s: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", s or "")

@app.after_request
def add_cors(response):
    response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN
    response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response

@app.route("/")
def home():
    return jsonify({"status": "OK"})

@app.route("/api/holehe")
def api_holehe():
    email = request.args.get("email", "").strip()
    if not email:
        return jsonify({"error": "Provide ?email=someone@example.com"}), 400
    try:
        proc = subprocess.run(
            ["holehe", email, "--no-color"],
            capture_output=True,
            text=True,
            timeout=60
        )
        raw_out = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")
        raw_out = raw_out.strip()
        raw_out = strip_ansi(raw_out)
        if len(raw_out) > MAX_OUTPUT_CHARS:
            raw_trunc = raw_out[:MAX_OUTPUT_CHARS] + "\n\n...output truncated..."
        else:
            raw_trunc = raw_out
        registered = []
        for line in raw_out.splitlines():
            line = line.strip()
            if line.startswith("[+]"):
                site = re.sub(r"^\[\+\]\s*", "", line).strip()
                if site and not site.lower().startswith("twitter :") and not site.lower().startswith("github :"):
                    registered.append(site)
        resp = {"email": email, "output": raw_trunc, "registered_on": registered, "count": len(registered)}
        r = make_response(jsonify(resp))
        r.headers["Content-Type"] = "application/json"
        return r
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Holehe scan timed out"}), 504
    except FileNotFoundError:
        return jsonify({"error": "holehe CLI not installed / not in PATH on server"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/breach")
def api_breach():
    term = request.args.get("term", "").strip()
    if not term:
        return jsonify({"error": "Provide ?term=someone@example.com or username"}), 400
    if not RAPIDAPI_KEY:
        return jsonify({"error": "RAPIDAPI_KEY not configured on server"}), 500
    url = f"https://breachdirectory.p.rapidapi.com/?func=auto&term={term}"
    headers = {
        "x-rapidapi-host": "breachdirectory.p.rapidapi.com",
        "x-rapidapi-key": RAPIDAPI_KEY,
        "accept": "application/json"
    }
    try:
        r = requests.get(url, headers=headers, timeout=30)
        content_type = r.headers.get("Content-Type", "")
        text = r.text
        if len(text) > MAX_OUTPUT_CHARS:
            text = text[:MAX_OUTPUT_CHARS] + "\n\n...truncated..."
        return make_response(text, r.status_code, {"Content-Type": content_type or "application/json"})
    except requests.RequestException as e:
        return jsonify({"error": "Upstream request failed", "details": str(e)}), 502

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
