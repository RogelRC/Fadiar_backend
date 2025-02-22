from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models.user import users
from config.db import conn
from cryptography.fernet import Fernet
import os

security = HTTPBearer()
FERNET_KEY = os.getenv("FERNET_KEY", "FF7J4NiWS7o1HfQMOcD4Hjz_6PgEvCODGCY0NPPoM_E=")
f = Fernet(FERNET_KEY.encode())


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        decrypted = f.decrypt(token.encode()).decode()
        email, _ = decrypted.split(":", 1)

        user = conn.execute(
            users.select().where(users.c.email == email)
        ).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

        return dict(user)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )