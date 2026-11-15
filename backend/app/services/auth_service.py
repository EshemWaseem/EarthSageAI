import re
import datetime
from datetime import timedelta
from typing import Tuple, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    generate_refresh_token,
    hash_token
)
from app.database.models import UserModel, RefreshTokenModel

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def signup(self, full_name: str, email: str, password: str) -> UserModel:
        """
        Validates, hashes password, and creates a new user.
        Rejects duplicates and weak passwords.
        """
        name = full_name.strip()
        clean_email = email.strip().lower()

        if len(name) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Full name must be at least 2 characters long."
            )

        if not EMAIL_REGEX.match(clean_email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please provide a valid email address."
            )

        if len(password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long."
            )

        # Check duplicate email
        existing = self.db.query(UserModel).filter(UserModel.email == clean_email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email address already exists."
            )

        password_hash = hash_password(password)
        user = UserModel(
            full_name=name,
            email=clean_email,
            password_hash=password_hash,
            is_active=True
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def login(self, email: str, password: str) -> Tuple[UserModel, str, str]:
        """
        Validates credentials, issues JWT access token and fresh refresh token.
        Returns: (user, access_token, raw_refresh_token)
        """
        clean_email = email.strip().lower()
        user = self.db.query(UserModel).filter(UserModel.email == clean_email).first()

        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This user account is inactive or disabled."
            )

        access_token = create_access_token(user_id=user.id, email=user.email)
        raw_refresh = generate_refresh_token()
        token_hash = hash_token(raw_refresh)
        expires_at = datetime.datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        refresh_record = RefreshTokenModel(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
            revoked=False
        )
        self.db.add(refresh_record)
        self.db.commit()

        return user, access_token, raw_refresh

    def refresh(self, raw_refresh_token: str) -> Tuple[UserModel, str, str]:
        """
        Rotates refresh token and issues a new access token.
        Detects reuse/revocation and revokes session on misuse.
        Returns: (user, new_access_token, new_raw_refresh_token)
        """
        if not raw_refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token is missing."
            )

        target_hash = hash_token(raw_refresh_token)
        record = self.db.query(RefreshTokenModel).filter(RefreshTokenModel.token_hash == target_hash).first()

        if not record:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or unrecognized refresh token."
            )

        # Detect reuse of revoked token (theft scenario)
        if record.revoked:
            # Revoke all refresh tokens for this compromised user
            self.db.query(RefreshTokenModel).filter(
                RefreshTokenModel.user_id == record.user_id
            ).update({"revoked": True})
            self.db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token was revoked or reused. All sessions terminated for security."
            )

        if record.expires_at < datetime.datetime.utcnow():
            record.revoked = True
            self.db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has expired. Please log in again."
            )

        user = self.db.query(UserModel).filter(UserModel.id == record.user_id).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is no longer active."
            )

        # Token Rotation: Revoke current token and issue fresh replacement
        record.revoked = True

        new_access_token = create_access_token(user_id=user.id, email=user.email)
        new_raw_refresh = generate_refresh_token()
        new_hash = hash_token(new_raw_refresh)
        expires_at = datetime.datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        new_record = RefreshTokenModel(
            user_id=user.id,
            token_hash=new_hash,
            expires_at=expires_at,
            revoked=False
        )
        self.db.add(new_record)
        self.db.commit()

        return user, new_access_token, new_raw_refresh

    def logout(self, raw_refresh_token: Optional[str]):
        """
        Revokes the refresh token session in database.
        """
        if not raw_refresh_token:
            return

        target_hash = hash_token(raw_refresh_token)
        record = self.db.query(RefreshTokenModel).filter(RefreshTokenModel.token_hash == target_hash).first()
        if record:
            record.revoked = True
            self.db.commit()

