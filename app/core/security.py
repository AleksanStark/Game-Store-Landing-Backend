from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from app.core.config import settings
import bcrypt



def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_access_token(admin_id: int):
    expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    payload = {"sub": str(admin_id), "type": "access", "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")



def create_refresh_token(admin_id: int) -> tuple[str, datetime]:
    expire = datetime.now(timezone.utc) + timedelta(days=30)
    payload = {"sub": str(admin_id), "type": "refresh", "exp": expire}
    token = jwt.encode(payload, settings.secret_key, algorithm="HS256")
    return token, expire


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    except JWTError:
        raise ValueError("Невалидный или истёкший токен")