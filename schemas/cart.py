from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class Cart(BaseModel):
    id: Optional[int] = None
    user_id: int
    product_id: int
    quantity: int = 1  # Por defecto, mínimo 1 unidad
    added_at: datetime = datetime.now()
    is_purchased: bool = False  # Nuevo atributo

class CartUpdate(BaseModel):
    quantity: int = Field(..., gt=0)  # Asegura que la cantidad sea mayor a 0