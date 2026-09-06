from flask import Flask, request, jsonify
import socket
import requests
import re

app = Flask(__name__)

def get_whois(domain):
    try:
        url = f"https://whoisjson.com/api/v1/whois?domain={domain}"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("whois", "غير متاح")[:300] + "..."
        else:
            return "تعذر جلب WHOIS"
    except:
        return "تعذر جلب WHOIS"

def analyze_target(url):
    try:
        domain = url.replace("https://", "").replace("http://", "").split("/")[0]
        ip = socket.gethostbyname(domain)
        whois_info = get_whois(domain)
        return {
            "domain": domain,
            "ip": ip,
            "whois": whois_info,
            "status": "تم التحليل بنجاح"
        }
    except Exception as e:
        return {"error": str(e)}

@app.route('/')
def root():
    return jsonify({"status": "Orchestrator Online", "agents": ["Scan", "Code", "Cloud"]})

@app.route('/api/v1/execute', methods=['POST'])
def execute_command():
    data = request.get_json()
    if not data or 'command' not in data:
        return jsonify({"data": "❌ أمر غير صحيح"}), 400
    cmd = data['command'].lower()
    if "تحليل" in cmd or "افحص" in cmd:
        url_match = re.search(r'(https?://[^\s]+)', data['command'])
        if not url_match:
            return jsonify({"data": "❌ لم أجد رابطاً صحيحاً في الأمر."})
        result = analyze_target(url_match.group(1))
        return jsonify({"data": result})
    else:
        return jsonify({"data": "⚠️ أمر غير معروف. استخدم: تحليل موقع https://example.com"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
