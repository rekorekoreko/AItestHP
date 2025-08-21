import time
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from .config import settings


def create_token(sub: str = "admin") -> str:
    payload = {"sub": sub, "exp": int(time.time()) + settings.jwt_ttl_seconds}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algo)


security = HTTPBearer()


def require_admin(creds: HTTPAuthorizationCredentials = Depends(security)) -> bool:
    token = creds.credentials
    try:
        jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algo])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return True


def verify_admin_password(pw: str) -> bool:
    return pw == settings.admin_password
