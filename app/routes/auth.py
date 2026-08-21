from fastapi import APIRouter, Depends, HTTPException, Response, Request
from app.core.database import get_connection
from app.core.security import (verify_password, create_access_token, create_refresh_token, hash_password)
from app.repositories.auth_repo import (get_admin_by_email, save_refresh_token, is_refresh_token_valid, revoke_refresh_token, create_admin)
from app.schemas.auth import LoginRequest, TokenResponse, RegisterRequest
from jose import jwt, JWTError
from app.core.config import settings
import asyncpg

router = APIRouter(prefix="/auth")

REFRESH_COOKIE_NAME = "refresh_token"


@router.post("/register", response_model=TokenResponse)
async def register(data: RegisterRequest, response: Response, conn: asyncpg.Connection = Depends(get_connection)):
    hashed_password = hash_password(data.password)
    admin_email = await create_admin(conn, data.email, hashed_password)


    admin = await get_admin_by_email(conn, str(admin_email["email"]))

    if not admin:
        raise HTTPException(status_code=500, detail="Регистрация не удалась попробуйте ввести данные снова")

    access_token = create_access_token(admin["id"])
    refresh_token, expires_at = create_refresh_token(admin["id"])

    await save_refresh_token(conn,admin["id"], refresh_token, expires_at)

    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite=None,
        max_age=30 * 24 * 60 * 60,
    )

    return TokenResponse(access_token=access_token)


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, response: Response, conn: asyncpg.Connection = Depends(get_connection)):
    admin = await get_admin_by_email(conn, data.email)

    if not admin or not verify_password(data.password, admin["password_hash"]):
        raise HTTPException(status_code=401, detail="Неверный email или пароль")

    access_token = create_access_token(admin["id"])
    refresh_token, expires_at = create_refresh_token(admin["id"])
    await save_refresh_token(conn, admin["id"], refresh_token, expires_at)

    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite=None,
        max_age=30 * 24 * 60 * 60,
    )

    return TokenResponse(access_token=access_token)

@router.post("/refresh", response_model=TokenResponse)
async def refresh(request: Request, conn: asyncpg.Connection=Depends(get_connection)):
    token = request.cookies.get(REFRESH_COOKIE_NAME)

    if not token:
        raise HTTPException(status_code=401, detail="Refresh token отстутствует")

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    except JWTError:
        raise HTTPException(status_code=401, detail="Невалидный refresh token")

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Неверный тип токена")

    admin_id = int(payload["sub"])

    if not await is_refresh_token_valid(conn, admin_id, token):
        raise HTTPException(status_code=401, detail="Токен отозван или истёк")

    new_access_token = create_access_token(admin_id)
    return TokenResponse(access_token=new_access_token)


@router.post("/logout")
async def logout(request: Request, response: Response, conn: asyncpg.Connection=Depends(get_connection)):
    token = request.cookies.get(REFRESH_COOKIE_NAME)
    if token:
        await revoke_refresh_token(conn, token)
    response.delete_cookie(REFRESH_COOKIE_NAME)
    return {"message": "Выход выполнен"}
