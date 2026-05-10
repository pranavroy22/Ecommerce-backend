from pydantic import BaseModel
from typing import List


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int


class OrderCreate(BaseModel):
    items: List[OrderItemCreate]


# 🔥 FIXED RESPONSE MODEL
class CheckoutResponse(BaseModel):
    order_id: int
    message: str
    total_price: float