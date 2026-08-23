from datetime import UTC, datetime
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..deps import get_current_user
from ..models import Inspector, RefreshToken, RoleEnum
from ..schemas import InspectorOut, InspectorRegister, LoginRequest, TokenPairResponse
from ..security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    hash_refresh_token,
    refresh_token_expiry,
    verify_password,
)
from ..utils.audit import add_audit_log

router = APIRouter(prefix='/auth', tags=['auth'])
REFRESH_COOKIE_NAME = 'refresh_token'

def _set_refresh_cookie(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite='lax',
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
        path='/auth',
    )

@router.post('/register', response_model=InspectorOut, status_code=status.HTTP_201_CREATED)
def register(payload: InspectorRegister, request: Request, db: Session = Depends(get_db)):
    existing = db.scalar(select(Inspector).where(Inspector.email == payload.email))
    if existing:
        raise HTTPException(status_code=400, detail='Пользователь с таким email уже существует')

    user = Inspector(
        full_name=payload.full_name,
        rank=payload.rank,
        phone=payload.phone,
        email=payload.email,
        role=payload.role,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.flush()

    add_audit_log(
        db,
        user_id=user.id,
        action='register',
        entity='inspector',
        entity_id=user.id,
        ip_address=request.client.host if request.client else None,
    )
    db.commit()
    db.refresh(user)
    return user

@router.post('/login', response_model=TokenPairResponse)
def login(payload: LoginRequest, response: Response, request: Request, db: Session = Depends(get_db)):
    user = db.scalar(select(Inspector).where(Inspector.email == payload.email))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail='Неверный email или пароль')

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token()
    db.add(
        RefreshToken(
            inspector_id=user.id,
            token_hash=hash_refresh_token(refresh_token),
            expires_at=refresh_token_expiry(),
            user_agent=request.headers.get('user-agent'),
            ip_address=request.client.host if request.client else None,
        )
    )

    add_audit_log(
        db,
        user_id=user.id,
        action='login',
        entity='auth',
        entity_id=user.id,
        ip_address=request.client.host if request.client else None,
    )

    db.commit()
    _set_refresh_cookie(response, refresh_token)
    return TokenPairResponse(access_token=access_token)

@router.post('/refresh', response_model=TokenPairResponse)
def refresh_token(response: Response, request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get(REFRESH_COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=401, detail='Refresh-токен отсутствует')

    token_hash = hash_refresh_token(token)
    token_row = db.scalar(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
    if not token_row or token_row.revoked_at is not None or token_row.expires_at <= datetime.now(UTC):
        raise HTTPException(status_code=401, detail='Refresh-токен недействителен')

    user = db.get(Inspector, token_row.inspector_id)
    if not user:
        raise HTTPException(status_code=401, detail='Пользователь не найден')

    token_row.revoked_at = datetime.now(UTC)

    new_refresh_token = create_refresh_token()
    db.add(
        RefreshToken(
            inspector_id=user.id,
            token_hash=hash_refresh_token(new_refresh_token),
            expires_at=refresh_token_expiry(),
            user_agent=request.headers.get('user-agent'),
            ip_address=request.client.host if request.client else None,
        )
    )
    db.commit()

    _set_refresh_cookie(response, new_refresh_token)
    return TokenPairResponse(access_token=create_access_token(str(user.id)))

@router.post('/logout', status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request, response: Response, db: Session = Depends(get_db), _: Inspector = Depends(get_current_user)):
    token = request.cookies.get(REFRESH_COOKIE_NAME)
    if token:
        token_hash = hash_refresh_token(token)
        token_row = db.scalar(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
        if token_row and token_row.revoked_at is None:
            token_row.revoked_at = datetime.now(UTC)
            db.commit()

    response.delete_cookie(REFRESH_COOKIE_NAME, path='/auth')
    return response
