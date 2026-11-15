"""Re-run the Lahore investigation pipeline with corrected analysis."""
import asyncio
import json
from app.database.connection import SessionLocal
from app.services.investigation_service import InvestigationService

async def rerun():
    db = SessionLocal()
    try:
        svc = InvestigationService(db)
        updated = svc.get_investigation_by_id("inv-20261114-30c9a0")
        if not updated:
            print("ERROR: Investigation not found!")
            return

        print(f"Current status: {updated.status}")
        print("Re-running pipeline with corrected analysis...")

        updated = await svc.run_investigation_pipeline("inv-20261114-30c9a0")

        print(f"\nNew status: {updated.status}")
        print(f"Findings count: {len(updated.findings)}")

        for f in updated.findings:
            print(f"\n--- Finding ---")
            print(f"Title: {f['title']}")
            print(f"Classification: {f['classification']}")
            print(f"Summary: {f['summary'][:300]}...")

        # Print autocorrelation audit from statistical metrics
        if updated.statistical_metrics:
            for param_key, param_stats in updated.statistical_metrics.items():
                trend = param_stats.get("trend", {})
                ac = trend.get("autocorrelation_audit", {})
                ann_mk = trend.get("annual_mann_kendall", {})
                print(f"\n=== {param_key} ===")
                print(f"Annual MK test used: {ann_mk.get('test_used', 'N/A')}")
                print(f"Annual MK p-value: {ann_mk.get('p_value', 'N/A')}")
                print(f"Annual MK tau: {ann_mk.get('kendall_tau', 'N/A')}")
                print(f"Annual Sen's slope: {ann_mk.get('sens_slope', 'N/A')}")
                if ac:
                    print(f"Autocorrelation lag-1 r: {ac.get('lag1_autocorrelation', 'N/A')}")
                    print(f"Ljung-Box Q: {ac.get('ljung_box_Q', 'N/A')}")
                    print(f"Ljung-Box p: {ac.get('ljung_box_p', 'N/A')}")
                    print(f"Correction method: {ac.get('correction_method', 'N/A')}")
                    print(f"Verdict: {ac.get('verdict', 'N/A')}")
    finally:
        db.close()

asyncio.run(rerun())

