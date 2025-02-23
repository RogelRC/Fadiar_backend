# schemas/cart.py
from pydantic import BaseModel
from datetime import datetime

class CartBase(BaseModel):
    product_id: int
    quantity: int

class CartCreate(CartBase):
    pass

class CartUpdate(BaseModel):
    quantity: int

class Cart(CartBase):
    id: int
    user_id: int
    is_purchased: bool
    added_at: datetime  # Add this line

    class Config:
        orm_mode = True