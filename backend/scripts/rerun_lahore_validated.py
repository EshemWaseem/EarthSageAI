"""
Re-run the Lahore investigation with the validated scientific methodology.
Updates PostgreSQL record inv-20261114-30c9a0 with day-weighted aggregation,
multi-lag autocorrelation audit, verified slope units, and zero fabricated scores.
"""
import asyncio
from app.database.connection import SessionLocal
from app.services.investigation_service import InvestigationService

async def main():
    db = SessionLocal()
    try:
        svc = InvestigationService(db)
        inv = svc.get_investigation_by_id("inv-20261114-30c9a0")
        if not inv:
            print("ERROR: Investigation inv-20261114-30c9a0 not found")
            return
            
        print(f"Executing validated pipeline for: {inv.id} ({inv.title})")
        updated = await svc.run_investigation_pipeline("inv-20261114-30c9a0")
        print(f"Status: {updated.status}")
        print(f"Findings Count: {len(updated.findings)}")
        for f in updated.findings:
            print(f"\n--- Finding: {f['title']} ---")
            print(f"Classification: {f['classification']}")
            print(f"Summary: {f['summary']}")
            for m in f.get("measurements", []):
                print(f"  {m['label']}: {m['value']} {m['unit']} ({m.get('uncertainty', '')})")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())

