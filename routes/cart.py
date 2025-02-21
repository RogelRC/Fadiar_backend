from typing import List
from fastapi import APIRouter, HTTPException
from models.cart import carts
from config.db import conn
from schemas.cart import Cart, CartUpdate  # Asegúrate de agregar CartUpdate en schemas/cart.py
import requests

cartt = APIRouter()


@cartt.get("/carts", response_model=List[Cart])
def get_carts():
    return conn.execute(carts.select()).fetchall()


@cartt.get("/carts/{id}", response_model=Cart)
def get_user(id: int):
    cart = conn.execute(carts.select().where(carts.c.id == id)).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart item not found")
    return cart


@cartt.post("/carts", response_model=Cart)
def create_cart(cart: Cart):
    url = "https://app.fadiar.com/api/inventory"
    response = requests.get(url)

    if response.status_code == 200:
        products = response.json().get("products", [])
        exists = any(
            product['id'] == cart.product_id and product['count'] >= cart.quantity
            for product in products
        )

        if exists:
            new_cart = {
                "user_id": cart.user_id,
                "product_id": cart.product_id,
                "quantity": cart.quantity
            }
            result = conn.execute(carts.insert().values(new_cart))
            return conn.execute(carts.select().where(carts.c.id == result.lastrowid)).first()
        else:
            raise HTTPException(status_code=400, detail="Product not available or insufficient stock")
    else:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch products from inventory")


@cartt.put("/carts/{cart_id}", response_model=Cart)
def update_cart_quantity(cart_id: int, cart_update: CartUpdate):
    # Obtener el carrito existente
    existing_cart = conn.execute(carts.select().where(carts.c.id == cart_id)).first()
    if not existing_cart:
        raise HTTPException(status_code=404, detail="Cart item not found")

    # Verificar el inventario
    url = "https://app.fadiar.com/api/inventory"
    response = requests.get(url)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch inventory")

    products = response.json().get("products", [])
    product = next((p for p in products if p['id'] == existing_cart.product_id), None)

    if not product:
        raise HTTPException(status_code=400, detail="Product no longer available")
    if product['count'] < cart_update.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")

    # Actualizar la cantidad en el carrito
    conn.execute(
        carts.update()
        .where(carts.c.id == cart_id)
        .values(quantity=cart_update.quantity)
    )

    # Devolver el carrito actualizado
    updated_cart = conn.execute(carts.select().where(carts.c.id == cart_id)).first()
    return updated_cart