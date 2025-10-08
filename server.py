from flask import Flask, request, jsonify, make_response
import subprocess, os, re, requests, json

app = Flask(__name__)
MAX_OUTPUT = 20000
RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY", "")

def strip_ansi(s):
    return re.sub(r'\x1b\[[0-9;]*m', '', s or '')

@app.after_request
def add_headers(resp):
    resp.headers['Access-Control-Allow-Origin'] = '*'  # restrict to your domain in production
    resp.headers['Access-Control-Allow-Methods'] = 'GET,OPTIONS'
    resp.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return resp

@app.route('/')
def home():
    return jsonify({"status":"Holehe proxy running"})

@app.route('/api/holehe')
def api_holehe():
    email = request.args.get('email','').strip()
    if not email:
        return jsonify({"error":"Provide ?email=someone@example.com"}), 400
    try:
        proc = subprocess.run(['holehe', email, '--no-color'], capture_output=True, text=True, timeout=60)
        out = (proc.stdout or '') + ("\n"+proc.stderr if proc.stderr else "")
        out = strip_ansi(out).strip()
        if len(out) > MAX_OUTPUT:
            out = out[:MAX_OUTPUT] + "\n\n...output truncated..."
        # filter registered lines
        registered = []
        for ln in out.splitlines():
            if ln.strip().startswith('[+]'):
                site = re.sub(r'^\[\+\]\s*','',ln).strip()
                if site and not site.lower().startswith('twitter :') and not site.lower().startswith('github :'):
                    registered.append(site)
        return make_response(json.dumps({"email":email,"output":out,"registered_on":registered,"count":len(registered)}),200,{'Content-Type':'application/json'})
    except subprocess.TimeoutExpired:
        return jsonify({"error":"Holehe timed out"}),504
    except FileNotFoundError:
        return jsonify({"error":"holehe CLI not installed on server"}),500
    except Exception as e:
        return jsonify({"error":str(e)}),500

@app.route('/api/breach')
def api_breach():
    term = request.args.get('term','').strip()
    if not term:
        return jsonify({"error":"Provide ?term=someone@example.com"}),400
    if not RAPIDAPI_KEY:
        return jsonify({"error":"RAPIDAPI_KEY not configured on server"}),500
    url = f'https://breachdirectory.p.rapidapi.com/?func=auto&term={term}'
    headers = {
        "x-rapidapi-host":"breachdirectory.p.rapidapi.com",
        "x-rapidapi-key":RAPIDAPI_KEY,
        "accept":"application/json"
    }
    try:
        r = requests.get(url, headers=headers, timeout=30)
        text = r.text
        if len(text) > MAX_OUTPUT:
            text = text[:MAX_OUTPUT] + "\n\n...truncated..."
        ct = r.headers.get('Content-Type','application/json')
        return make_response(text, r.status_code, {'Content-Type':ct})
    except requests.RequestException as e:
        return jsonify({"error":"Upstream request failed","details":str(e)}),502

if __name__=='__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
