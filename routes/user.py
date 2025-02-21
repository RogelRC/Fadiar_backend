import random

from fastapi import APIRouter, HTTPException
from config.db import conn
from schemas.token import Token
from schemas.user import User
from typing import List
from models.user import users
from cryptography.fernet import Fernet
from schemas.user import UserLogin
from utils.send_verification_mail import send_verification_email
from datetime import datetime, timedelta

user = APIRouter()

key = Fernet.generate_key()
f = Fernet(key)

@user.get("/users", response_model=List[User])
def get_users():
    return conn.execute(users.select()).fetchall()

@user.get("/users/{id}", response_model=User)
def get_user(id: int):
    return conn.execute(users.select().where(users.c.id == id)).first()

@user.post("/users", response_model=User)
def create_user(user: User):
    verification_code = random.randint(100000, 999999)  # Código de 4 dígitos
    new_user = {
        "username": user.username,
        "email": user.email,
        "verified": False,
        "password": f.encrypt(user.password.encode("utf-8")),
        "verification_code": verification_code,
        "verification_code_created_at": datetime.now()  # Registrar timestamp
    }

    send_verification_email(user.email, f"{new_user['verification_code']}")  # Comillas simples
    result = conn.execute(users.insert().values(new_user))

    return conn.execute(users.select().where(users.c.id == result.lastrowid)).first()


@user.post("/verify")
def verify_code(email: str, code: int):
    user = conn.execute(users.select().where(users.c.email == email)).first()

    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    expiration_time = user.verification_code_created_at + timedelta(minutes=15)

    if datetime.now() > expiration_time:
        raise HTTPException(status_code=410, detail="Código expirado")

    if user.verification_code != code:
        raise HTTPException(status_code=400, detail="Código inválido")

    # Marcar usuario como verificado
    conn.execute(users.update()
                 .where(users.c.email == email)
                 .values(verified=True, verification_code=None))

    return {"message": "Cuenta verificada exitosamente"}


# Para reenvío de código (si el usuario solicita nuevo código)
@user.post("/resend-code")
def resend_code(email: str):
    # Invalidar código anterior
    new_code = random.randint(100000, 999999)

    conn.execute(users.update()
    .where(users.c.email == email)
    .values(
        verification_code=new_code,
        verification_code_created_at=datetime.now()
    ))

    send_verification_email(email, new_code)
    return {"message": "Nuevo código enviado"}


@user.post("/login", response_model=Token)
def login(user_data: UserLogin):
    user = conn.execute(users.select().where(users.c.email == user_data.email)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    decrypted_password = f.decrypt(user.password).decode("utf-8")
    if decrypted_password != user_data.password:
        raise HTTPException(status_code=400, detail="Contraseña incorrecta")

    token_data = f"{user.email}:{datetime.now()}"
    auth_token = f.encrypt(token_data.encode()).decode()

    return {"token": auth_token}


@user.get("/me", response_model=User)
def get_current_user(token: str):
    try:
        decrypted_token = f.decrypt(token.encode()).decode()
        email, _ = decrypted_token.split(":", 1)
    except:
        raise HTTPException(status_code=401, detail="Token inválido")

    user = conn.execute(users.select().where(users.c.email == email)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return user