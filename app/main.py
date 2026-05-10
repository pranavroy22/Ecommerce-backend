from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine
from app import models
from app.routers import users, products, orders, cart
from app.routers import ai
from app.routers import payment

# =========================
# APP INIT
# =========================
app = FastAPI(
    title="Ecommerce API",
    version="1.0.0"
)


# =========================
# CORS (VERY IMPORTANT)
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 🔥 for development (frontend can access)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# CREATE TABLES (DEV ONLY)
# =========================
models.Base.metadata.create_all(bind=engine)


# =========================
# ROUTERS
# =========================
app.include_router(users.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(cart.router)
app.include_router(ai.router)
app.include_router(payment.router)
# =========================
# ROOT ENDPOINT
# =========================
@app.get("/")
def home():
    return {
        "message": "Ecommerce API running 🚀"
    }