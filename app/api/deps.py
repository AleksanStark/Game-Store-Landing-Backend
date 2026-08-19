from fastapi import Depends, HTTPException, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError, ExpiredSignatureError
from app.core.config import settings

security = HTTPBearer()

async def get_current_admin_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:


    token = credentials.credentials

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Токен истёк")

    except JWTError:
        raise HTTPException(status_code=401, detail="Невалидный")

    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Неверный тип токена")

    return int(payload["sub"])