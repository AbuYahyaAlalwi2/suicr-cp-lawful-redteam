python
import socket
import whois
import requests

def analyze_website(url):
    try:
        domain = url.replace("https://", "").replace("http://", "").split("/")[0]
        ip = socket.gethostbyname(domain)
        w = whois.whois(domain)
        headers = requests.get(f"https://{domain}", timeout=5).headers
        return {
            "domain": domain,
            "ip": ip,
            "server": headers.get("Server", "غير معروف"),
            "whois": w.text[:300],
            "status": "تم التحليل"
        }
    except Exception as e:
        return {"error": str(e)}

def scan_ports(domain):
    try:
        ip = socket.gethostbyname(domain)
        common_ports = [21, 22, 23, 25, 80, 443, 3306, 3389, 5432, 8080]
        open_ports = []
        for port in common_ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((ip, port))
            if result == 0:
                open_ports.append(port)
            sock.close()
        return open_ports
    except Exception as e:
        return {"error": str(e)}
