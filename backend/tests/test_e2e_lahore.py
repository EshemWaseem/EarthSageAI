import urllib.request
import json

def run_test():
    payload = {
        "title": "Lahore Meteorological Trend Analysis (1991-2020)",
        "research_question": "Has surface 2m temperature exhibited significant warming in Lahore between 1991 and 2020?",
        "hypothesis": "MERRA-2 assimilation data indicates a statistically significant upward temperature trend.",
        "location_name": "Lahore",
        "region": "Punjab",
        "country": "Pakistan",
        "latitude": 31.5497,
        "longitude": 74.3436,
        "start_year": 1991,
        "end_year": 2020,
        "parameters": ["T2M", "PRECTOTCORR"]
    }

    req = urllib.request.Request(
        "http://localhost:8020/api/v1/investigations",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    res = urllib.request.urlopen(req)
    created = json.loads(res.read().decode())
    inv_id = created["id"]
    print(f"Created Investigation: {inv_id}")

    # Run pipeline
    run_req = urllib.request.Request(
        f"http://localhost:8020/api/v1/investigations/{inv_id}/run",
        data=b"",
        headers={"Content-Type": "application/json"}
    )
    run_res = urllib.request.urlopen(run_req)
    completed = json.loads(run_res.read().decode())

    print(f"Pipeline Status: {completed['status']}")
    print(f"Time Series Points: {len(completed['timeSeriesData'])}")
    print("Scientific Findings:")
    for f in completed["findings"]:
        print(f"  * {f['title']}")
        print(f"    Summary: {f['summary']}")
        for m in f.get("measurements", []):
            print(f"    - {m['label']}: {m['value']} {m['unit']} ({m['uncertainty']})")

    # Generate Report
    rep_req = urllib.request.Request(
        "http://localhost:8020/api/v1/reports",
        data=json.dumps({"investigation_id": inv_id, "file_format": "PDF"}).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    rep_res = urllib.request.urlopen(rep_req)
    report = json.loads(rep_res.read().decode())
    print(f"Generated Report: {report['id']} ({report['fileFormat']}, {report['fileSize']})")

if __name__ == "__main__":
    run_test()

