from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import UserModel
from app.services.auth_service import AuthService
from app.core.config import settings
from app.api.deps import get_current_user

router = APIRouter(tags=["auth"])

class SignupRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=150, description="User's full name")
    email: EmailStr = Field(..., description="Valid work/academic email address")
    password: str = Field(..., min_length=8, max_length=128, description="Secure password (minimum 8 characters)")

class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="Registered email address")
    password: str = Field(..., min_length=1, description="Account password")

class RefreshRequest(BaseModel):
    refresh_token: Optional[str] = Field(None, description="Optional fallback refresh token if cookie is not sent")

class UserResponse(BaseModel):
    id: str
    fullName: str
    email: str
    isActive: bool
    createdAt: str

class AuthResponse(BaseModel):
    accessToken: str
    tokenType: str = "Bearer"
    user: UserResponse

def _format_user_response(user: UserModel) -> UserResponse:
    return UserResponse(
        id=user.id,
        fullName=user.full_name,
        email=user.email,
        isActive=user.is_active,
        createdAt=user.created_at.isoformat() + "Z" if user.created_at else ""
    )

def _set_refresh_cookie(response: Response, raw_refresh_token: str) -> None:
    response.set_cookie(
        key=settings.AUTH_COOKIE_NAME,
        value=raw_refresh_token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        httponly=True,
        secure=settings.AUTH_COOKIE_SECURE,
        samesite=settings.AUTH_COOKIE_SAMESITE,
        path="/"
    )

def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(
        key=settings.AUTH_COOKIE_NAME,
        path="/",
        httponly=True,
        samesite=settings.AUTH_COOKIE_SAMESITE
    )

@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=AuthResponse)
def signup(payload: SignupRequest, response: Response, db: Session = Depends(get_db)):
    """
    Registers a new researcher or analyst.
    Issues JWT access token and sets HttpOnly refresh cookie upon successful registration.
    """
    service = AuthService(db)
    user = service.signup(
        full_name=payload.full_name,
        email=payload.email,
        password=payload.password
    )
    
    # Auto-login newly registered user
    user, access_token, refresh_token = service.login(
        email=payload.email,
        password=payload.password
    )
    
    _set_refresh_cookie(response, refresh_token)

    return AuthResponse(
        accessToken=access_token,
        tokenType="Bearer",
        user=_format_user_response(user)
    )

@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    """
    Authenticates user credentials.
    Returns short-lived JWT access token in body and sets secure HttpOnly cookie for refresh token.
    """
    service = AuthService(db)
    user, access_token, refresh_token = service.login(
        email=payload.email,
        password=payload.password
    )

    _set_refresh_cookie(response, refresh_token)

    return AuthResponse(
        accessToken=access_token,
        tokenType="Bearer",
        user=_format_user_response(user)
    )

@router.post("/refresh", response_model=AuthResponse)
def refresh(
    request: Request,
    response: Response,
    body: Optional[RefreshRequest] = None,
    db: Session = Depends(get_db)
):
    """
    Rotates refresh token and issues a new access token.
    Reads refresh token from HttpOnly cookie (or body fallback).
    """
    cookie_token = request.cookies.get(settings.AUTH_COOKIE_NAME)
    body_token = body.refresh_token if body else None
    token_to_use = cookie_token or body_token

    if not token_to_use:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is required via cookie or request body."
        )

    service = AuthService(db)
    user, new_access, new_refresh = service.refresh(token_to_use)

    _set_refresh_cookie(response, new_refresh)

    return AuthResponse(
        accessToken=new_access,
        tokenType="Bearer",
        user=_format_user_response(user)
    )

@router.post("/logout")
def logout(
    request: Request,
    response: Response,
    body: Optional[RefreshRequest] = None,
    db: Session = Depends(get_db)
):
    """
    Revokes the current session refresh token in database and clears the refresh cookie.
    """
    cookie_token = request.cookies.get(settings.AUTH_COOKIE_NAME)
    body_token = body.refresh_token if body else None
    token_to_revoke = cookie_token or body_token

    if token_to_revoke:
        service = AuthService(db)
        service.logout(token_to_revoke)

    _clear_refresh_cookie(response)
    return {"message": "Logged out successfully."}

@router.get("/me", response_model=UserResponse)
def get_me(current_user: UserModel = Depends(get_current_user)):
    """
    Returns current authenticated user profile.
    Requires Bearer JWT access token.
    """
    return _format_user_response(current_user)

