from sqlalchemy import Table, Column, Integer, String, Boolean, DateTime
from config.db import meta

users = Table(
    "users",
    meta,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("username", String(255), nullable=False),
    Column("email", String(255), unique=True, nullable=False),
    Column("password", String(255), nullable=False),
    Column("verification_code", Integer, nullable=True),
    Column("verified", Boolean, nullable=False, default=False),
    Column("verification_code_created_at", DateTime, nullable=True)  # Nuevo campo
)
