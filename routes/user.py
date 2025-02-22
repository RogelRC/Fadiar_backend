import random
from fastapi import APIRouter, HTTPException, status, Depends
from config.db import conn
from models.user import users
from schemas.user import (
    UserCreate,
    UserResponse,
    UserLogin,
    VerifyRequest,
    ResendCodeRequest,
    UpdatePasswordRequest
)
from schemas.token import Token
from cryptography.fernet import Fernet
from utils.send_verification_mail import send_verification_email
from datetime import datetime, timedelta
from utils.auth import get_current_user
import os

user_router = APIRouter()

# Configuración de Fernet
FERNET_KEY = os.getenv("FERNET_KEY", "FF7J4NiWS7o1HfQMOcD4Hjz_6PgEvCODGCY0NPPoM_E=")
f = Fernet(FERNET_KEY.encode())


# Registro de usuario
@user_router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    # Verificar si el email ya existe
    existing_user = conn.execute(
        users.select().where(users.c.email == user_data.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )

    verification_code = random.randint(100000, 999999)
    new_user = {
        "username": user_data.username,
        "email": user_data.email,
        "password": f.encrypt(user_data.password.encode()),
        "verified": False,
        "verification_code": verification_code,
        "verification_code_created_at": datetime.now(),
        "created_at": datetime.now()
    }

    try:
        send_verification_email(user_data.email, verification_code)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al enviar el correo de verificación"
        )

    result = conn.execute(users.insert().values(new_user))
    return conn.execute(users.select().where(users.c.id == result.lastrowid)).first()


# Verificación de email
@user_router.post("/verify")
async def verify_email(verify_data: VerifyRequest):
    user = conn.execute(
        users.select().where(users.c.email == verify_data.email)
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    if user.verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La cuenta ya está verificada"
        )

    expiration_time = user.verification_code_created_at + timedelta(minutes=15)
    if datetime.now() > expiration_time:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Código expirado"
        )

    if user.verification_code != verify_data.code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Código inválido"
        )

    conn.execute(
        users.update()
        .where(users.c.email == verify_data.email)
        .values(verified=True, verification_code=None)
    )

    return {"message": "Cuenta verificada exitosamente"}


# Reenvío de código
@user_router.post("/resend-code")
async def resend_verification_code(resend_data: ResendCodeRequest):
    user = conn.execute(
        users.select().where(users.c.email == resend_data.email)
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    if user.verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La cuenta ya está verificada"
        )

    new_code = random.randint(100000, 999999)
    conn.execute(
        users.update()
        .where(users.c.email == resend_data.email)
        .values(
            verification_code=new_code,
            verification_code_created_at=datetime.now()
        )
    )

    try:
        send_verification_email(resend_data.email, new_code)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al reenviar el código"
        )

    return {"message": "Nuevo código de verificación enviado"}


# Login de usuario
@user_router.post("/login", response_model=Token)
async def login(login_data: UserLogin):
    user = conn.execute(
        users.select().where(users.c.email == login_data.email)
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    try:
        decrypted_password = f.decrypt(user.password).decode()
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al descifrar la contraseña"
        )

    if decrypted_password != login_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
        )

    if not user.verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cuenta no verificada"
        )

    token_data = f"{user.email}:{datetime.now()}"
    auth_token = f.encrypt(token_data.encode()).decode()

    return {"token": auth_token, "token_type": "bearer"}


# Cambio de contraseña
@user_router.put("/update-password")
async def update_password(
        update_data: UpdatePasswordRequest,
        current_user: dict = Depends(get_current_user)
):
    stored_password = f.decrypt(current_user["password"]).decode()

    if stored_password != update_data.current_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Contraseña actual incorrecta"
        )

    if stored_password == update_data.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La nueva contraseña debe ser diferente"
        )

    encrypted_password = f.encrypt(update_data.new_password.encode())
    conn.execute(
        users.update()
        .where(users.c.id == current_user["id"])
        .values(password=encrypted_password)
    )

    return {"message": "Contraseña actualizada exitosamente"}