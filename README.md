# 🌐 NetTools — Networking Project

A combined web app demonstrating two core networking concepts:
1. **File Transfer over HTTP** (TCP-based client-server)
2. **DNS Lookup & Traceroute** (DNS protocol + ICMP routing)

---

## 🚀 Setup & Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# Also install traceroute if on Linux
sudo apt install traceroute   # Ubuntu/Debian
# brew install traceroute     # macOS

# 2. Run the server
python app.py

# 3. Open in browser
# http://localhost:5000
```

---

## 📁 Project Structure

```
nettools/
├── app.py               ← Flask backend (all networking logic)
├── requirements.txt     ← Python dependencies
├── uploads/             ← Uploaded files stored here
└── templates/
    └── index.html       ← Frontend UI
```

---

## 🔬 Networking Concepts Covered

### 1. File Transfer (TCP / HTTP)
- The browser connects to the Flask server using **HTTP over TCP**
- Files are sent as **multipart/form-data** (standard HTTP upload format)
- TCP guarantees **reliable, ordered delivery** — crucial for file integrity
- The server stores files and serves them back via **HTTP GET** (download)

### 2. DNS Lookup
- **DNS (Domain Name System)** translates human-readable domains (e.g. `google.com`) into IP addresses
- Uses the `dnspython` library to query DNS servers for multiple **record types**:
  - `A` — IPv4 address
  - `AAAA` — IPv6 address
  - `MX` — Mail server
  - `NS` — Nameservers
  - `TXT` — Text records (SPF, verification, etc.)
  - `CNAME` — Canonical name (alias)

### 3. Traceroute (ICMP / Routing)
- Traceroute sends packets with incrementing **TTL (Time To Live)** values
- Each router that drops a packet (TTL=0) sends back an **ICMP Time Exceeded** message
- By collecting these replies, we map the **path packets take** across the internet
- Shows each **hop's IP address** and **round-trip time (RTT)**

---

## 🛠 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/upload` | Upload a file |
| GET | `/files` | List all uploaded files |
| GET | `/download/<filename>` | Download a file |
| DELETE | `/delete/<filename>` | Delete a file |
| POST | `/dns` | DNS record lookup |
| POST | `/traceroute` | Run traceroute |
