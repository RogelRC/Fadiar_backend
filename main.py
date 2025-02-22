from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.db import meta, engine
from routes.user import user_router
from routes.cart import cart_router


meta.create_all(engine)

app = FastAPI(debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción cambiar a dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)
app.include_router(cart_router)

