from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.db import meta, engine
from routes.user import user
from routes.cart import cartt


meta.create_all(engine)

app = FastAPI(debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción cambiar a dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user)
app.include_router(cartt)

