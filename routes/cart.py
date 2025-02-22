from typing import List
from fastapi import APIRouter, HTTPException, Depends, status
from models.cart import carts
from config.db import conn
from schemas.cart import Cart, CartCreate, CartUpdate
from utils.auth import get_current_user
import requests

cart_router = APIRouter()

INVENTORY_SERVICE = "http://localhost:8000"  # Ajustar según tu entorno


@cart_router.get("/carts", response_model=List[Cart])
def get_user_carts(current_user: dict = Depends(get_current_user)):
    return conn.execute(
        carts.select().where(carts.c.user_id == current_user["id"])
    ).fetchall()


@cart_router.post("/carts", response_model=Cart)
def create_cart(
        cart_data: CartCreate,
        current_user: dict = Depends(get_current_user)
):
    # Verificar inventario
    inventory_url = f"{INVENTORY_SERVICE}/inventory/{cart_data.product_id}"
    try:
        response = requests.get(inventory_url)
        response.raise_for_status()
        product = response.json()

        if product["count"] < cart_data.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Stock insuficiente"
            )

    except requests.exceptions.RequestException:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Error al verificar inventario"
        )

    # Crear item en carrito
    new_cart = {
        "user_id": current_user["id"],
        "product_id": cart_data.product_id,
        "quantity": cart_data.quantity
    }

    result = conn.execute(carts.insert().values(new_cart))
    return conn.execute(carts.select().where(carts.c.id == result.lastrowid)).first()


@cart_router.put("/carts/{cart_id}", response_model=Cart)
def update_cart_quantity(
        cart_id: int,
        cart_update: CartUpdate,
        current_user: dict = Depends(get_current_user)
):
    # Verificar que el carrito pertenece al usuario
    existing_cart = conn.execute(
        carts.select().where(
            (carts.c.id == cart_id) &
            (carts.c.user_id == current_user["id"])
        )
    ).first()

    if not existing_cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item no encontrado"
        )

    # Verificar inventario
    inventory_url = f"{INVENTORY_SERVICE}/inventory/{existing_cart.product_id}"
    try:
        response = requests.get(inventory_url)
        response.raise_for_status()
        product = response.json()

        if product["count"] < cart_update.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Stock insuficiente"
            )

    except requests.exceptions.RequestException:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Error al verificar inventario"
        )

    # Actualizar cantidad
    conn.execute(
        carts.update()
        .where(carts.c.id == cart_id)
        .values(quantity=cart_update.quantity)
    )

    return conn.execute(carts.select().where(carts.c.id == cart_id)).first()