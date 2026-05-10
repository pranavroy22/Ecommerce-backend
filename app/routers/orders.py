from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.services import order_service
from app.schemas.order import CheckoutResponse

from app.dependencies import get_current_user
from app import models
from app.database import get_db

router = APIRouter(prefix="/orders", tags=["Orders"])


# =========================
# CHECKOUT (MAIN FLOW)
# =========================
@router.post("/checkout", response_model=CheckoutResponse)
def checkout(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    order_id, total_price = order_service.checkout(db, current_user)

    return {
        "message": "Order placed successfully",
        "order_id": order_id,
        "total_price": total_price
    }


# =========================
# GET USER ORDERS
# =========================
@router.get("/my")
def get_my_orders(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    orders = db.query(models.Order).filter(
        models.Order.user_id == current_user.id
    ).all()

    result = []

    for order in orders:
        result.append({
            "order_id": order.id,
            "status": order.status,
            "payment_status": order.payment_status,
            "items": [
                {
                    "product_id": item.product_id,
                    "quantity": item.quantity
                }
                for item in order.items
            ]
        })

    return result


# =========================
# GET ALL ORDERS (ADMIN)
# =========================
@router.get("/")
def get_all_orders(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    return db.query(models.Order).all()


# =========================
# UPDATE ORDER STATUS (ADMIN)
# =========================
@router.put("/{order_id}/status")
def update_order_status(
    order_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    order = db.query(models.Order).filter(
        models.Order.id == order_id
    ).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can update")

    if order.payment_status != "success":
        raise HTTPException(status_code=400, detail="Order not paid yet")

    allowed_status = ["pending", "paid", "shipped", "delivered", "cancelled"]

    if status not in allowed_status:
        raise HTTPException(status_code=400, detail="Invalid status")

    order.status = status
    db.commit()

    return {"message": f"Order status updated to {status}"}


# =========================
# PAY FOR ORDER (USER)
# =========================
@router.post("/{order_id}/pay")
def pay_for_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    order = order_service.pay_for_order(db, current_user, order_id)

    return {
        "message": "Payment successful",
        "order_id": order.id,
        "status": order.status,
        "payment_status": order.payment_status
    }