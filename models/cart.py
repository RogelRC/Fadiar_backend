from sqlalchemy import Table, Column, Integer, ForeignKey, TIMESTAMP, Boolean
from datetime import datetime
from config.db import meta

carts = Table(
    "cart",
    meta,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("product_id", Integer, nullable=False),
    Column("quantity", Integer, nullable=False, default=1),
    Column("added_at", TIMESTAMP, nullable=False, default=datetime.now()),
    Column("is_purchased", Boolean, nullable=False, default=False)  # Nueva columna
)