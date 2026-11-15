#!/usr/bin/env python3
"""
EarthSage AI — Comprehensive Authentication Security & Authorization Audit Script
Conducts rigorous automated tests covering all 6 validation areas:
1. Cross-user investigation isolation (403 Forbidden)
2. Cross-user pipeline execution blocking (403 Forbidden)
3. Cross-user report generation blocking (403 Forbidden)
4. Cross-user report downloading blocking with guessed IDs (403 Forbidden)
5. Unauthenticated private resource download blocking (403 Forbidden)
6. Analysis and AI explanation isolation (403 Forbidden)
7. Request body user_id injection prevention (ID bound strictly to JWT sub)
8. Baseline investigation accessibility according to documented policy
9. JWT signature verification, expiration enforcement, and algorithm restriction
10. Refresh token rotation, replay attack detection, and session-wide mass revocation
11. Inactive user authentication lockout (403/401)
12. Zero exposure of password hashes or raw refresh tokens in API payloads
13. Cookie attribute compliance (HttpOnly, SameSite, Path, Max-Age)
"""

import sys
import uuid
import datetime
import httpx
import jwt

BASE_URL = "http://localhost:8020"

def log_audit(test_num: int, name: str, passed: bool, detail: str = ""):
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] Test {test_num:02d}: {name}")
    if detail:
        print(f"        └─ {detail}")
    if not passed:
        print("\nAUDIT FAILED: Security check did not meet strict compliance.")
        sys.exit(1)

def run_security_audit():
    print("=" * 80)
    print("EARTHSAGE AI — STRICT SECURITY & AUTHORIZATION AUDIT ENGINE")
    print(f"Target: {BASE_URL}")
    print("=" * 80)

    client = httpx.Client(base_url=BASE_URL, timeout=45.0)

    # Setup User A (Dr. Alice Smith)
    suffix_a = uuid.uuid4().hex[:6]
    email_a = f"alice_{suffix_a}@earthscience.org"
    pwd_a = "PasswordAlice@2026!"
    res_a = client.post("/api/auth/signup", json={"full_name": "Dr. Alice Smith", "email": email_a, "password": pwd_a})
    assert res_a.status_code == 201, f"User A signup failed: {res_a.text}"
    user_a = res_a.json()["user"]
    token_a = res_a.json()["accessToken"]
    cookie_a = res_a.cookies.get("earthsage_refresh_token")
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Setup User B (Dr. Bob Jones)
    suffix_b = uuid.uuid4().hex[:6]
    email_b = f"bob_{suffix_b}@earthscience.org"
    pwd_b = "PasswordBob@2026!"
    res_b = client.post("/api/auth/signup", json={"full_name": "Dr. Bob Jones", "email": email_b, "password": pwd_b})
    assert res_b.status_code == 201, f"User B signup failed: {res_b.text}"
    user_b = res_b.json()["user"]
    token_b = res_b.json()["accessToken"]
    cookie_b = res_b.cookies.get("earthsage_refresh_token")
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 1. Zero Exposure of Password Hashes or Raw Tokens
    has_hash_in_a = "password_hash" in str(res_a.json()) or "password" in res_a.json().get("user", {})
    has_raw_refresh_in_body = "refresh_token" in res_a.json() or "token_hash" in str(res_a.json())
    log_audit(
        1,
        "Zero Exposure of Password Hashes & Raw Tokens in API Payloads",
        not has_hash_in_a and not has_raw_refresh_in_body,
        f"Signup response contains keys: {list(res_a.json().keys())}; user keys: {list(user_a.keys())}"
    )

    # 2. Cookie Security Attributes
    set_cookie_header = res_a.headers.get("set-cookie", "")
    is_httponly = "httponly" in set_cookie_header.lower()
    has_samesite = "samesite=lax" in set_cookie_header.lower()
    has_path = "path=/" in set_cookie_header.lower()
    has_max_age = "max-age=" in set_cookie_header.lower()
    log_audit(
        2,
        "Cookie Security Attributes (HttpOnly, SameSite, Path, Max-Age)",
        is_httponly and has_samesite and has_path and has_max_age,
        f"Cookie Header: {set_cookie_header[:80]}..."
    )

    # 3. User A Creates Private Investigation (Test user_id injection prevention)
    injected_user_id = str(uuid.uuid4())
    create_inv_payload = {
        "title": f"Alice Cryosphere Audit ({suffix_a})",
        "research_question": "Does temperature trend indicate significant warming in Alice's sector?",
        "location_name": "Skardu",
        "latitude": 35.2971,
        "longitude": 75.6333,
        "start_year": 1991,
        "end_year": 2020,
        "parameters": ["T2M"],
        "user_id": injected_user_id # Malicious injection attempt
    }
    create_res = client.post("/api/v1/investigations", json=create_inv_payload, headers=headers_a)
    assert create_res.status_code == 200, f"Investigation creation failed: {create_res.text}"
    inv_a = create_res.json()
    inv_a_id = inv_a["id"]
    actual_bound_id = inv_a.get("userId")
    log_audit(
        3,
        "Strict JWT Sub Binding & Injection Prevention (Request body user_id ignored)",
        actual_bound_id == user_a["id"] and actual_bound_id != injected_user_id,
        f"Bound user_id: {actual_bound_id} (Matches JWT: {user_a['id']}, Ignored injected: {injected_user_id})"
    )

    # 4. User B Cannot Read User A's Private Investigation (403 Forbidden)
    get_a_by_b = client.get(f"/api/v1/investigations/{inv_a_id}", headers=headers_b)
    log_audit(
        4,
        "Cross-User Investigation Read Isolation (GET /investigations/{id})",
        get_a_by_b.status_code == 403,
        f"HTTP Status: {get_a_by_b.status_code}, Detail: {get_a_by_b.json().get('detail')}"
    )

    # 5. User B Cannot Run User A's Investigation Pipeline (403 Forbidden)
    run_a_by_b = client.post(f"/api/v1/investigations/{inv_a_id}/run", headers=headers_b)
    log_audit(
        5,
        "Cross-User Pipeline Execution Blocking (POST /investigations/{id}/run)",
        run_a_by_b.status_code == 403,
        f"HTTP Status: {run_a_by_b.status_code}, Detail: {run_a_by_b.json().get('detail')}"
    )

    # 6. User B Cannot Generate Reports for User A's Investigation (403 Forbidden)
    gen_by_b = client.post(
        "/api/v1/reports",
        json={"investigation_id": inv_a_id, "file_format": "PDF"},
        headers=headers_b
    )
    log_audit(
        6,
        "Cross-User Report Generation Blocking (POST /reports)",
        gen_by_b.status_code == 403,
        f"HTTP Status: {gen_by_b.status_code}, Detail: {gen_by_b.json().get('detail')}"
    )

    # 7. User A Generates PDF & CSV Reports
    gen_pdf_a = client.post(
        "/api/v1/reports",
        json={"investigation_id": inv_a_id, "file_format": "PDF"},
        headers=headers_a
    )
    assert gen_pdf_a.status_code == 200, f"PDF report generation failed: {gen_pdf_a.text}"
    report_pdf_id = gen_pdf_a.json()["id"]

    gen_csv_a = client.post(
        "/api/v1/reports",
        json={"investigation_id": inv_a_id, "file_format": "CSV"},
        headers=headers_a
    )
    assert gen_csv_a.status_code == 200, f"CSV report generation failed: {gen_csv_a.text}"
    report_csv_id = gen_csv_a.json()["id"]
    log_audit(
        7,
        "Authorized Report Generation & Author Attribution",
        gen_pdf_a.json()["author"] == "Dr. Alice Smith" and gen_csv_a.json()["author"] == "Dr. Alice Smith",
        f"PDF Report ID: {report_pdf_id}, CSV Report ID: {report_csv_id}, Author: {gen_pdf_a.json()['author']}"
    )

    # 8. User B Cannot Download User A's Reports Using Guessed Report IDs (403 Forbidden)
    dl_pdf_by_b = client.get(f"/api/v1/reports/{report_pdf_id}/download", headers=headers_b)
    dl_csv_by_b = client.get(f"/api/v1/reports/{report_csv_id}/download", headers=headers_b)
    log_audit(
        8,
        "Cross-User Report Download Blocking via Guessed IDs (GET /reports/{id}/download)",
        dl_pdf_by_b.status_code == 403 and dl_csv_by_b.status_code == 403,
        f"PDF DL Status: {dl_pdf_by_b.status_code}, CSV DL Status: {dl_csv_by_b.status_code}"
    )

    # 9. Unauthenticated User Cannot Download User A's Reports (403 Forbidden)
    dl_pdf_unauth = client.get(f"/api/v1/reports/{report_pdf_id}/download")
    dl_csv_unauth = client.get(f"/api/v1/reports/{report_csv_id}/download")
    log_audit(
        9,
        "Unauthenticated Private Report Download Blocking (GET /reports/{id}/download)",
        dl_pdf_unauth.status_code == 403 and dl_csv_unauth.status_code == 403,
        f"Unauth PDF DL: {dl_pdf_unauth.status_code}, Unauth CSV DL: {dl_csv_unauth.status_code}"
    )

    # 10. User A Can Download Their Own PDF and CSV Reports (200 OK)
    dl_pdf_by_a = client.get(f"/api/v1/reports/{report_pdf_id}/download", headers=headers_a)
    dl_csv_by_a = client.get(f"/api/v1/reports/{report_csv_id}/download", headers=headers_a)
    is_valid_pdf = dl_pdf_by_a.content.startswith(b"%PDF")
    is_valid_csv = "# EARTHSAGE AI" in dl_csv_by_a.text
    log_audit(
        10,
        "Authorized Owner Report Downloading (PDF Binary & Commented CSV)",
        dl_pdf_by_a.status_code == 200 and dl_csv_by_a.status_code == 200 and is_valid_pdf and is_valid_csv,
        f"PDF Magic: {dl_pdf_by_a.content[:5]}, CSV Header present: {is_valid_csv}"
    )

    # 11. Cross-User Analysis & AI Route Isolation (403 Forbidden)
    anom_by_b = client.get(f"/api/v1/analysis/investigations/{inv_a_id}/anomalies", headers=headers_b)
    comp_by_b = client.get(f"/api/v1/analysis/investigations/{inv_a_id}/compare", headers=headers_b)
    ai_by_b = client.post(f"/api/v1/ai/explain/{inv_a_id}", headers=headers_b)
    log_audit(
        11,
        "Cross-User Analysis & AI Endpoint Isolation (/anomalies, /compare, /ai/explain)",
        anom_by_b.status_code == 403 and comp_by_b.status_code == 403 and ai_by_b.status_code == 403,
        f"Anomalies: {anom_by_b.status_code}, Compare: {comp_by_b.status_code}, AI Explain: {ai_by_b.status_code}"
    )

    # 12. Baseline Investigation & Report Policy Compliance
    base_inv = client.get("/api/v1/investigations/inv-20261114-30c9a0", headers=headers_a)
    base_inv_b = client.get("/api/v1/investigations/inv-20261114-30c9a0", headers=headers_b)
    log_audit(
        12,
        "Baseline Investigation Universally Readable (inv-20261114-30c9a0)",
        base_inv.status_code == 200 and base_inv_b.status_code == 200,
        f"User A Status: {base_inv.status_code}, User B Status: {base_inv_b.status_code}"
    )

    # 13. Refresh Token Rotation & Replay Attack Mass Revocation
    refresh_res = client.post("/api/auth/refresh", cookies={"earthsage_refresh_token": cookie_a})
    assert refresh_res.status_code == 200
    new_token_a = refresh_res.json()["accessToken"]
    new_cookie_a = refresh_res.cookies.get("earthsage_refresh_token")
    rotated_ok = new_cookie_a is not None and new_cookie_a != cookie_a

    # Replay of revoked cookie_a -> Must be rejected with 401
    replay_res = client.post("/api/auth/refresh", cookies={"earthsage_refresh_token": cookie_a})
    replay_rejected = replay_res.status_code == 401

    # Security check: After replay theft detection, the active session is also revoked
    compromised_res = client.post("/api/auth/refresh", cookies={"earthsage_refresh_token": new_cookie_a})
    all_sessions_revoked = compromised_res.status_code == 401
    log_audit(
        13,
        "Refresh Token Rotation & Replay Theft Mass Revocation",
        rotated_ok and replay_rejected and all_sessions_revoked,
        f"Rotated: {rotated_ok}, Replay Rejected (401): {replay_rejected}, User Sessions Terminated: {all_sessions_revoked}"
    )

    # 14. Inactive User Authentication Lockout
    inactive_email = f"inactive_{uuid.uuid4().hex[:6]}@earthscience.org"
    inact_pwd = "InactiveUserPass@2026"
    inact_res = client.post("/api/auth/signup", json={"full_name": "Disabled Researcher", "email": inactive_email, "password": inact_pwd})
    assert inact_res.status_code == 201
    inact_token = inact_res.json()["accessToken"]
    inact_cookie = inact_res.cookies.get("earthsage_refresh_token")
    inact_id = inact_res.json()["user"]["id"]

    # Deactivate in database via direct SQL in container
    from app.database.connection import SessionLocal
    from app.database.models import UserModel
    db = SessionLocal()
    u = db.query(UserModel).filter(UserModel.id == inact_id).first()
    u.is_active = False
    db.commit()
    db.close()

    inact_login = client.post("/api/auth/login", json={"email": inactive_email, "password": inact_pwd})
    inact_me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {inact_token}"})
    inact_ref = client.post("/api/auth/refresh", cookies={"earthsage_refresh_token": inact_cookie})
    log_audit(
        14,
        "Inactive/Disabled User Authentication Lockout (Login: 403, /me: 403, Refresh: 401)",
        inact_login.status_code == 403 and inact_me.status_code == 403 and inact_ref.status_code == 401,
        f"Login: {inact_login.status_code}, /me: {inact_me.status_code}, Refresh: {inact_ref.status_code}"
    )

    # 15. JWT Algorithm Tampering & Signature Validation
    # Attempting to forge token with "none" algorithm
    unsecured_token = jwt.encode({"sub": user_b["id"], "type": "access", "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)}, "", algorithm="none")
    tampered_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {unsecured_token}"})
    
    # Attempting to forge token with wrong secret
    wrong_secret_token = jwt.encode({"sub": user_b["id"], "type": "access", "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)}, "wrong-secret-key-12345", algorithm="HS256")
    wrong_secret_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {wrong_secret_token}"})

    # Attempting to use expired token
    expired_token = jwt.encode({"sub": user_b["id"], "type": "access", "exp": datetime.datetime.utcnow() - datetime.timedelta(hours=1)}, "earthsage-jwt-secret-key-development-mode-2026-secure-random", algorithm="HS256")
    expired_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {expired_token}"})

    log_audit(
        15,
        "JWT Tampering, 'none' Algorithm & Expiration Rejection",
        tampered_res.status_code == 401 and wrong_secret_res.status_code == 401 and expired_res.status_code == 401,
        f"none Algorithm: {tampered_res.status_code}, Wrong Secret: {wrong_secret_res.status_code}, Expired: {expired_res.status_code}"
    )

    print("=" * 80)
    print("ALL 15 STRICT SECURITY & AUTHORIZATION AUDIT CHECKS PASSED (100% COMPLIANT)")
    print("=" * 80)

if __name__ == "__main__":
    run_security_audit()

