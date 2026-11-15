import urllib.request
import json

res1 = urllib.request.urlopen('http://localhost:8020/api/v1/analysis/investigations/inv-20261114-30c9a0/anomalies', timeout=30)
data1 = json.loads(res1.read().decode())
print('Anomalies status: 200, parameters:', list(data1['anomalies'].keys()))
for p, a in data1['anomalies'].items():
    top_z = a['detected_anomalies'][0]['standardized_z_score'] if a['detected_anomalies'] else 'none'
    top_date = a['detected_anomalies'][0]['date'] if a['detected_anomalies'] else 'none'
    print(f"  {p}: total={a['total_observations']}, anomalies={a['anomaly_count']}, top anomaly={top_date} (Z={top_z})")

res2 = urllib.request.urlopen('http://localhost:8020/api/v1/analysis/investigations/inv-20261114-30c9a0/compare?param_a=T2M&param_b=PRECTOTCORR', timeout=30)
data2 = json.loads(res2.read().decode())
comp = data2['comparison']
print('Comparison status: 200, sample size:', comp['sample_size'])
print('  Spearman rho:', comp['spearman_rank_correlation']['coefficient_rho'], 'p-val:', comp['spearman_rank_correlation']['p_value'])
print('  Pearson r:   ', comp['pearson_correlation']['coefficient_r'], 'p-val:', comp['pearson_correlation']['p_value'])

# Test CSV Report Generation
req_csv = urllib.request.Request(
    'http://localhost:8020/api/v1/reports',
    data=json.dumps({'investigation_id': 'inv-20261114-30c9a0', 'file_format': 'CSV'}).encode(),
    headers={'Content-Type': 'application/json'}
)
res_csv = urllib.request.urlopen(req_csv, timeout=10)
csv_rep = json.loads(res_csv.read().decode())
print(f"CSV Report generated: ID={csv_rep['id']}, Format={csv_rep['fileFormat']}, Size={csv_rep['fileSize']}")

# Test Download CSV
res_dl = urllib.request.urlopen(f"http://localhost:8020/api/v1/reports/{csv_rep['id']}/download", timeout=10)
csv_text = res_dl.read().decode()
print(f"CSV Download: Status={res_dl.status}, Lines={len(csv_text.splitlines())}")
print("First 3 lines of CSV:")
for line in csv_text.splitlines()[:3]:
    print("  ", line)

