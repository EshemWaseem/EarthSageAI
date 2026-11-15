"""Cross-validate DB values against API response and verify corrected text."""
import json
import urllib.request

# Fetch the investigation from API
req = urllib.request.Request("http://localhost:8020/api/v1/investigations/inv-20261114-30c9a0")
res = urllib.request.urlopen(req, timeout=10)
inv = json.loads(res.read().decode())

print("=== CROSS-VALIDATION ===\n")
print(f"Status: {inv.get('status')}")
print(f"Title: {inv.get('title')}")

# Check findings text for forbidden terms
forbidden = ["seasonal redistribution", "seasonal re-distribution", "intra-annual seasonal shift",
             "intra-annual redistribution", "station", "ground station", "thermistor"]
clean = True
findings = inv.get("findings", [])
for f in findings:
    title = f.get("title", "")
    summary = f.get("summary", "")
    for term in forbidden:
        if term.lower() in title.lower():
            print(f"WARNING: Forbidden term '{term}' found in finding title: {title}")
            clean = False
        if term.lower() in summary.lower():
            print(f"WARNING: Forbidden term '{term}' found in finding summary")
            clean = False

if clean:
    print("PASS: No forbidden terminology in findings.")

print(f"\nFindings count: {len(findings)}")
for f in findings:
    print(f"\nTitle: {f['title']}")
    print(f"Classification: {f['classification']}")
    for m in f.get("measurements", []):
        print(f"  {m['label']}: {m['value']} {m['unit']} ({m.get('uncertainty', '')})")

# Check time series count
ts = inv.get("time_series_data", inv.get("timeSeriesData", []))
print(f"\nTime series points: {len(ts)}")

# Check statistical metrics for autocorrelation audit
sm = inv.get("statistical_metrics", inv.get("statisticalMetrics", {}))
if sm:
    for pk, ps in sm.items():
        trend = ps.get("trend", {})
        ac = trend.get("autocorrelation_audit", {})
        ann = trend.get("annual_mann_kendall", {})
        print(f"\n{pk} Annual MK test: {ann.get('test_used', 'N/A')}")
        print(f"{pk} Annual MK p: {ann.get('p_value', 'N/A')}")
        print(f"{pk} Autocorrelation correction: {ac.get('correction_method', 'N/A')}")
else:
    print("\nWARNING: No statistical metrics in API response")

