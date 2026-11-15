"""Generate a corrected PDF report."""
import json
import urllib.request

# Generate new report
data = json.dumps({"investigation_id": "inv-20261114-30c9a0", "file_format": "PDF"}).encode("utf-8")
req = urllib.request.Request(
    "http://localhost:8020/api/v1/reports",
    data=data,
    headers={"Content-Type": "application/json"}
)
try:
    res = urllib.request.urlopen(req, timeout=30)
    rep = json.loads(res.read().decode())
    print(f"Report ID: {rep.get('id')}")
    print(f"File size: {rep.get('fileSize', rep.get('file_size', 'N/A'))}")
    print(f"Format: {rep.get('fileFormat', rep.get('file_format', 'N/A'))}")
    print(f"Status: {rep.get('status', 'N/A')}")
    print("PDF report generated successfully.")
except Exception as e:
    print(f"Error: {e}")

