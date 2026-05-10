from sqlalchemy.orm import Session
from fastapi import HTTPException
from app import models
import random


def checkout(db: Session, current_user):
    cart = db.query(models.Cart).filter(
        models.Cart.user_id == current_user.id
    ).first()

    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    total_price = 0
    products_data = []

    for item in cart.items:
        product = db.query(models.Product).filter(
            models.Product.id == item.product_id
        ).first()

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        if product.stock < item.quantity:
            raise HTTPException(status_code=400, detail="Not enough stock")

        products_data.append((product, item))
        total_price += product.price * item.quantity

    new_order = models.Order(user_id=current_user.id)
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    for product, item in products_data:
        product.stock -= item.quantity

        db.add(models.OrderItem(
            order_id=new_order.id,
            product_id=item.product_id,
            quantity=item.quantity
        ))

    db.query(models.CartItem).filter(
        models.CartItem.cart_id == cart.id
    ).delete()

    db.commit()

    return new_order.id, total_price



# =========================
# PAYMENT (SIMULATION)
# =========================
def pay_for_order(db: Session, current_user, order_id: int):

    order = db.query(models.Order).filter(
        models.Order.id == order_id,
        models.Order.user_id == current_user.id
    ).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.payment_status == "success":
        raise HTTPException(status_code=400, detail="Order already paid")

    # Simulate payment success (75% success rate)
    success = random.choice([True, True, True, False])

    if not success:
        order.payment_status = "failed"
        db.commit()
        raise HTTPException(status_code=400, detail="Payment failed")

    # Update order
    order.payment_status = "success"
    order.status = "paid"

    db.commit()

    return order