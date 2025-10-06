from flask import Flask, request, jsonify
import subprocess
import re

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({"status": "Holehe API is running ✅"})

@app.route("/holehe")
def holehe_lookup():
    email = request.args.get("email")
    if not email:
        return jsonify({"error": "Please provide an email parameter like ?email=someone@example.com"}), 400

    try:
        
        result = subprocess.run(
            ["holehe", email, "--no-color"],
            capture_output=True,
            text=True,
            timeout=60
        )

        output = result.stdout.strip()
        if not output:
            output = result.stderr.strip() or "No output"

        
        lines = output.splitlines()
        registered_sites = []

        for line in lines:
            line = line.strip()
            if line.startswith("[+]"):
                # for site name
                match = re.search(r"\[\+\]\s*(.+)", line)
                if match:
                    site = match.group(1).strip()
                    
                    site = re.sub(r"\x1b\[[0-9;]*m", "", site)
                    registered_sites.append(site)

        
        registered_sites = [
            site for site in registered_sites
            if not any(x in site.lower() for x in ["twitter", "github", "btc"])
        ]

        return jsonify({
            "email": email,
            "registered_on": registered_sites,
            "count": len(registered_sites)
        })

    except subprocess.TimeoutExpired:
        return jsonify({"error": "Holehe scan timed out"}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
