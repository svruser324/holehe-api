from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

@app.route('/api/info')
def info():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    try:
        r = requests.get(f'https://ipapi.co/{ip}/json/', timeout=5)
        j = r.json()
        country = j.get('country_name', 'Unknown')
        region = j.get('region', 'Unknown')
        city = j.get('city', 'Unknown')
        isp = j.get('org', 'Unknown')
        lat = j.get('latitude', 'Unknown')
        lon = j.get('longitude', 'Unknown')
    except:
        country = region = city = isp = lat = lon = 'Unknown'
    return jsonify({
        'IP Address (WAN)': ip,
        'Country': country,
        'Region': region,
        'City': city,
        'Latitude': lat,
        'Longitude': lon,
        'ISP': isp
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
