from fastapi import APIRouter

import os

import razorpay


router = APIRouter(
    prefix="/payment",
    tags=["Payment"]
)


# 🔥 RAZORPAY CLIENT
client = razorpay.Client(
    auth=(
        os.getenv("RAZORPAY_KEY_ID"),
        os.getenv("RAZORPAY_KEY_SECRET")
    )
)


@router.post("/create-order")
def create_order(data: dict):

    amount = data.get("amount")

    order = client.order.create({

        "amount": int(amount * 100),  # paisa

        "currency": "INR",

        "payment_capture": 1
    })

    return order