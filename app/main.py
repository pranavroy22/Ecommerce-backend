from fastapi import FastAPI
from .database import engine
from . import models
from .routers import users
from .routers import products
from .routers import orders

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(users.router)
app.include_router(products.router)
app.include_router(orders.router)

@app.get("/")
def home():
    return {"message": "Ecommerce API running"}