from flask import Flask, request, jsonify, send_from_directory, render_template
import socket
import dns.resolver
import subprocess
import os
import uuid
import platform

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ── Home ──────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")

# ── File Transfer ─────────────────────────────────────────────────────────────
@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    f = request.files["file"]
    if f.filename == "":
        return jsonify({"error": "Empty filename"}), 400
    ext = os.path.splitext(f.filename)[1]
    unique_name = str(uuid.uuid4()) + ext
    save_path = os.path.join(UPLOAD_FOLDER, unique_name)
    f.save(save_path)
    size = os.path.getsize(save_path)
    return jsonify({
        "message": "File uploaded successfully",
        "original_name": f.filename,
        "saved_as": unique_name,
        "size_bytes": size,
        "download_url": f"/download/{unique_name}"
    })

@app.route("/files", methods=["GET"])
def list_files():
    files = []
    for fname in os.listdir(UPLOAD_FOLDER):
        path = os.path.join(UPLOAD_FOLDER, fname)
        files.append({
            "name": fname,
            "size_bytes": os.path.getsize(path),
            "download_url": f"/download/{fname}"
        })
    return jsonify(files)

@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

@app.route("/delete/<filename>", methods=["DELETE"])
def delete_file(filename):
    path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(path):
        os.remove(path)
        return jsonify({"message": "Deleted"})
    return jsonify({"error": "File not found"}), 404

# ── DNS Lookup ────────────────────────────────────────────────────────────────
@app.route("/dns", methods=["POST"])
def dns_lookup():
    data = request.get_json()
    domain = data.get("domain", "").strip()
    if not domain:
        return jsonify({"error": "Domain required"}), 400

    results = {}
    record_types = ["A", "AAAA", "MX", "NS", "TXT", "CNAME"]
    resolver = dns.resolver.Resolver()

    for rtype in record_types:
        try:
            answers = resolver.resolve(domain, rtype)
            results[rtype] = [str(r) for r in answers]
        except Exception:
            results[rtype] = []

    # Basic IP resolve
    try:
        ip = socket.gethostbyname(domain)
        results["resolved_ip"] = ip
    except Exception:
        results["resolved_ip"] = "Could not resolve"

    return jsonify({"domain": domain, "records": results})

# ── Traceroute ────────────────────────────────────────────────────────────────
@app.route("/traceroute", methods=["POST"])
def traceroute():
    data = request.get_json()
    domain = data.get("domain", "").strip()
    if not domain:
        return jsonify({"error": "Domain required"}), 400

    # Safety: only allow valid hostnames
    import re
    if not re.match(r'^[a-zA-Z0-9.\-]+$', domain):
        return jsonify({"error": "Invalid domain"}), 400

    system = platform.system()
    if system == "Windows":
        cmd = ["tracert", "-d", "-h", "15", domain]
    else:
        cmd = ["traceroute", "-m", "15", "-n", domain]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        output = result.stdout or result.stderr
        hops = parse_traceroute(output, system)
        return jsonify({"domain": domain, "hops": hops, "raw": output})
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Traceroute timed out"}), 504
    except FileNotFoundError:
        return jsonify({"error": "traceroute not installed on this system"}), 500

def parse_traceroute(output, system):
    hops = []
    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue
        import re
        # Match lines starting with a hop number
        match = re.match(r'^(\d+)\s+(.+)', line)
        if match:
            hop_num = match.group(1)
            rest = match.group(2)
            # Extract IP or * * *
            ips = re.findall(r'\d+\.\d+\.\d+\.\d+', rest)
            times = re.findall(r'[\d.]+\s*ms', rest)
            hops.append({
                "hop": int(hop_num),
                "ip": ips[0] if ips else "*",
                "times": times[:3] if times else ["*"]
            })
    return hops

if __name__ == "__main__":
    print("🌐 NetTools running at http://localhost:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)
