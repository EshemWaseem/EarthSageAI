import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.database.connection import get_db, SessionLocal
from app.database.models import UserModel, RefreshTokenModel, InvestigationModel, ReportModel
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    generate_refresh_token,
    hash_token
)
from app.core.config import settings

client = TestClient(app)

@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_password_hashing():
    pwd = "EarthScience@2026!"
    hashed = hash_password(pwd)
    assert hashed != pwd
    assert hashed.startswith("$2b$") or hashed.startswith("$argon2")
    assert verify_password(pwd, hashed) is True
    assert verify_password("WrongPassword123", hashed) is False

def test_jwt_token_generation_and_decoding():
    user_id = str(uuid.uuid4())
    email = "researcher@nasaspaceapps.org"
    token = create_access_token(user_id, email)
    
    assert isinstance(token, str)
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == user_id
    assert payload["email"] == email
    assert payload["type"] == "access"
    
    # Tampered token
    assert decode_access_token(token + "tampered") is None

def test_refresh_token_hashing():
    raw_token = generate_refresh_token()
    assert len(raw_token) >= 32
    hashed_1 = hash_token(raw_token)
    hashed_2 = hash_token(raw_token)
    assert len(hashed_1) == 64  # SHA-256 hex length
    assert hashed_1 == hashed_2

def test_auth_signup_flow(db_session: Session):
    random_email = f"user_{uuid.uuid4().hex[:8]}@earthscience.org"
    payload = {
        "full_name": "Dr. Sarah Khan",
        "email": random_email,
        "password": "SecurePassword@123"
    }

    response = client.post("/api/auth/signup", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "accessToken" in data
    assert data["user"]["email"] == random_email
    assert data["user"]["fullName"] == "Dr. Sarah Khan"
    assert settings.AUTH_COOKIE_NAME in response.cookies

    # Duplicate email rejection (409 Conflict)
    dup_res = client.post("/api/auth/signup", json=payload)
    assert dup_res.status_code == 409

    # Clean up
    created_user = db_session.query(UserModel).filter(UserModel.email == random_email).first()
    if created_user:
        db_session.query(RefreshTokenModel).filter(RefreshTokenModel.user_id == created_user.id).delete()
        db_session.delete(created_user)
        db_session.commit()

def test_auth_login_and_me_flow(db_session: Session):
    unique_email = f"login_test_{uuid.uuid4().hex[:8]}@earthscience.org"
    pwd = "CorrectPassword@2026"
    
    # Sign up
    signup_res = client.post("/api/auth/signup", json={
        "full_name": "Test Login User",
        "email": unique_email,
        "password": pwd
    })
    assert signup_res.status_code == 201

    # Login with incorrect password -> 401
    bad_login = client.post("/api/auth/login", json={
        "email": unique_email,
        "password": "WrongPassword!"
    })
    assert bad_login.status_code == 401

    # Login with correct password -> 200
    good_login = client.post("/api/auth/login", json={
        "email": unique_email,
        "password": pwd
    })
    assert good_login.status_code == 200
    login_data = good_login.json()
    token = login_data["accessToken"]
    assert token is not None
    assert settings.AUTH_COOKIE_NAME in good_login.cookies

    # Test GET /api/auth/me with valid Bearer token
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["email"] == unique_email
    assert me_data["fullName"] == "Test Login User"

    # Test GET /api/auth/me without Bearer token -> 401
    unauth_res = client.get("/api/auth/me")
    assert unauth_res.status_code == 401

    # Clean up
    user = db_session.query(UserModel).filter(UserModel.email == unique_email).first()
    if user:
        db_session.query(RefreshTokenModel).filter(RefreshTokenModel.user_id == user.id).delete()
        db_session.delete(user)
        db_session.commit()

def test_refresh_token_rotation_and_revocation(db_session: Session):
    user_email = f"refresh_test_{uuid.uuid4().hex[:8]}@earthscience.org"
    pwd = "PasswordForRefresh123!"

    # Sign up
    signup_res = client.post("/api/auth/signup", json={
        "full_name": "Refresh Tester",
        "email": user_email,
        "password": pwd
    })
    assert signup_res.status_code == 201
    initial_cookie = signup_res.cookies.get(settings.AUTH_COOKIE_NAME)
    assert initial_cookie is not None

    # Call refresh endpoint with cookie
    client.cookies.set(settings.AUTH_COOKIE_NAME, initial_cookie)
    refresh_res = client.post("/api/auth/refresh")
    assert refresh_res.status_code == 200
    refresh_data = refresh_res.json()
    assert "accessToken" in refresh_data
    new_cookie = refresh_res.cookies.get(settings.AUTH_COOKIE_NAME)
    assert new_cookie is not None
    assert new_cookie != initial_cookie

    # Replaying the OLD revoked cookie should trigger reuse detection and fail
    client.cookies.clear()
    reuse_res = client.post("/api/auth/refresh", cookies={settings.AUTH_COOKIE_NAME: initial_cookie})
    assert reuse_res.status_code == 401

    # Logout flow
    client.cookies.clear()
    logout_res = client.post("/api/auth/logout", cookies={settings.AUTH_COOKIE_NAME: new_cookie})
    assert logout_res.status_code == 200

    # Clean up
    user = db_session.query(UserModel).filter(UserModel.email == user_email).first()
    if user:
        db_session.query(RefreshTokenModel).filter(RefreshTokenModel.user_id == user.id).delete()
        db_session.delete(user)
        db_session.commit()

def test_investigation_ownership_and_isolation(db_session: Session):
    # Create User A
    user_a_email = f"usera_{uuid.uuid4().hex[:8]}@earthscience.org"
    res_a = client.post("/api/auth/signup", json={
        "full_name": "User Alpha",
        "email": user_a_email,
        "password": "PasswordAlpha123!"
    })
    token_a = res_a.json()["accessToken"]

    # Create User B
    user_b_email = f"userb_{uuid.uuid4().hex[:8]}@earthscience.org"
    res_b = client.post("/api/auth/signup", json={
        "full_name": "User Beta",
        "email": user_b_email,
        "password": "PasswordBeta123!"
    })
    token_b = res_b.json()["accessToken"]

    # User A creates an investigation
    inv_payload = {
        "title": "User Alpha Private Investigation",
        "research_question": "Does temperature exhibit trend in Alpha Study Area?",
        "location_name": "Lahore",
        "latitude": 31.5497,
        "longitude": 74.3436,
        "start_year": 1991,
        "end_year": 2020,
        "parameters": ["T2M"]
    }
    create_res = client.post(
        "/api/v1/investigations",
        json=inv_payload,
        headers={"Authorization": f"Bearer {token_a}"}
    )
    assert create_res.status_code == 200
    inv_id = create_res.json()["id"]

    # User A can get their own investigation
    get_res_a = client.get(f"/api/v1/investigations/{inv_id}", headers={"Authorization": f"Bearer {token_a}"})
    assert get_res_a.status_code == 200

    # User B tries to get User A's private investigation -> 403 Forbidden
    get_res_b = client.get(f"/api/v1/investigations/{inv_id}", headers={"Authorization": f"Bearer {token_b}"})
    assert get_res_b.status_code == 403

    # User B tries to run User A's private investigation -> 403 Forbidden
    run_res_b = client.post(f"/api/v1/investigations/{inv_id}/run", headers={"Authorization": f"Bearer {token_b}"})
    assert run_res_b.status_code == 403

    # Both User A and User B can access baseline study (user_id is None)
    baseline_inv = db_session.query(InvestigationModel).filter(InvestigationModel.user_id.is_(None)).first()
    if baseline_inv:
        base_res_a = client.get(f"/api/v1/investigations/{baseline_inv.id}", headers={"Authorization": f"Bearer {token_a}"})
        assert base_res_a.status_code == 200
        base_res_b = client.get(f"/api/v1/investigations/{baseline_inv.id}", headers={"Authorization": f"Bearer {token_b}"})
        assert base_res_b.status_code == 200

    # Clean up
    db_session.query(InvestigationModel).filter(InvestigationModel.id == inv_id).delete()
    user_a = db_session.query(UserModel).filter(UserModel.email == user_a_email).first()
    user_b = db_session.query(UserModel).filter(UserModel.email == user_b_email).first()
    if user_a:
        db_session.query(RefreshTokenModel).filter(RefreshTokenModel.user_id == user_a.id).delete()
        db_session.delete(user_a)
    if user_b:
        db_session.query(RefreshTokenModel).filter(RefreshTokenModel.user_id == user_b.id).delete()
        db_session.delete(user_b)
    db_session.commit()

def test_cross_user_report_access_and_guessed_id_rejection(db_session: Session):
    # User A setup
    email_a = f"author_a_{uuid.uuid4().hex[:8]}@earthscience.org"
    res_a = client.post("/api/auth/signup", json={
        "full_name": "Author Alpha",
        "email": email_a,
        "password": "PasswordAlpha123!"
    })
    token_a = res_a.json()["accessToken"]

    # User B setup
    email_b = f"author_b_{uuid.uuid4().hex[:8]}@earthscience.org"
    res_b = client.post("/api/auth/signup", json={
        "full_name": "Author Beta",
        "email": email_b,
        "password": "PasswordBeta123!"
    })
    token_b = res_b.json()["accessToken"]

    # User A creates a private investigation
    inv_payload = {
        "title": "Private Research Report Study",
        "research_question": "Does regional temperature change affect local glacier mass?",
        "location_name": "Lahore",
        "latitude": 31.5497,
        "longitude": 74.3436,
        "start_year": 1991,
        "end_year": 2020,
        "parameters": ["T2M"]
    }
    create_inv = client.post("/api/v1/investigations", json=inv_payload, headers={"Authorization": f"Bearer {token_a}"})
    inv_id = create_inv.json()["id"]

    # User B attempts to generate report for User A's investigation -> 403 Forbidden
    bad_gen = client.post(
        "/api/v1/reports",
        json={"investigation_id": inv_id, "file_format": "PDF"},
        headers={"Authorization": f"Bearer {token_b}"}
    )
    assert bad_gen.status_code == 403

    # User A generates a PDF report for their own investigation -> 200 OK
    good_gen = client.post(
        "/api/v1/reports",
        json={"investigation_id": inv_id, "file_format": "PDF"},
        headers={"Authorization": f"Bearer {token_a}"}
    )
    assert good_gen.status_code == 200
    report_id = good_gen.json()["id"]

    # User B attempts to download User A's report using guessed report ID -> 403 Forbidden
    dl_b = client.get(f"/api/v1/reports/{report_id}/download", headers={"Authorization": f"Bearer {token_b}"})
    assert dl_b.status_code == 403

    # Unauthenticated user attempts to download User A's report -> 403 Forbidden
    dl_unauth = client.get(f"/api/v1/reports/{report_id}/download")
    assert dl_unauth.status_code == 403

    # User A downloads their own report -> 200 OK
    dl_a = client.get(f"/api/v1/reports/{report_id}/download", headers={"Authorization": f"Bearer {token_a}"})
    assert dl_a.status_code == 200
    assert dl_a.content.startswith(b"%PDF")

    # User B attempts to access analysis endpoints for User A's private investigation -> 403 Forbidden
    anom_b = client.get(f"/api/v1/analysis/investigations/{inv_id}/anomalies", headers={"Authorization": f"Bearer {token_b}"})
    assert anom_b.status_code == 403

    comp_b = client.get(f"/api/v1/analysis/investigations/{inv_id}/compare", headers={"Authorization": f"Bearer {token_b}"})
    assert comp_b.status_code == 403

    explain_b = client.post(f"/api/v1/ai/explain/{inv_id}", headers={"Authorization": f"Bearer {token_b}"})
    assert explain_b.status_code == 403

    # Clean up
    db_session.query(ReportModel).filter(ReportModel.id == report_id).delete()
    db_session.query(InvestigationModel).filter(InvestigationModel.id == inv_id).delete()
    user_a = db_session.query(UserModel).filter(UserModel.email == email_a).first()
    user_b = db_session.query(UserModel).filter(UserModel.email == email_b).first()
    if user_a:
        db_session.query(RefreshTokenModel).filter(RefreshTokenModel.user_id == user_a.id).delete()
        db_session.delete(user_a)
    if user_b:
        db_session.query(RefreshTokenModel).filter(RefreshTokenModel.user_id == user_b.id).delete()
        db_session.delete(user_b)
    db_session.commit()

def test_inactive_user_cannot_authenticate(db_session: Session):
    inactive_email = f"inactive_{uuid.uuid4().hex[:8]}@earthscience.org"
    pwd = "InactiveUserPassword@2026"
    
    # Sign up
    signup_res = client.post("/api/auth/signup", json={
        "full_name": "Inactive Researcher",
        "email": inactive_email,
        "password": pwd
    })
    assert signup_res.status_code == 201
    active_token = signup_res.json()["accessToken"]
    cookie = signup_res.cookies.get(settings.AUTH_COOKIE_NAME)

    # Deactivate user in database
    user = db_session.query(UserModel).filter(UserModel.email == inactive_email).first()
    user.is_active = False
    db_session.commit()

    # 1. Login attempt by inactive user -> 403 Forbidden
    login_res = client.post("/api/auth/login", json={"email": inactive_email, "password": pwd})
    assert login_res.status_code == 403

    # 2. Existing token on /me by inactive user -> 403 Forbidden
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {active_token}"})
    assert me_res.status_code == 403

    # 3. Refresh attempt by inactive user -> 401 Unauthorized
    refresh_res = client.post("/api/auth/refresh", cookies={settings.AUTH_COOKIE_NAME: cookie})
    assert refresh_res.status_code == 401

    # Clean up
    db_session.query(RefreshTokenModel).filter(RefreshTokenModel.user_id == user.id).delete()
    db_session.delete(user)
    db_session.commit()

