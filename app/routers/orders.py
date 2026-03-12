from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..dependencies import get_current_user

from .. import models, schemas
from ..database import get_db

router = APIRouter()



@router.post("/orders")
def create_order(
    order: schemas.OrderCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    new_order = models.Order(user_id=current_user.id)

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    for item in order.items:

        product = db.query(models.Product).filter(
            models.Product.id == item.product_id
        ).first()

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        if product.stock < item.quantity:
            raise HTTPException(status_code=400, detail="Not enough stock")

        product.stock -= item.quantity

        order_item = models.OrderItem(
            order_id=new_order.id,
            product_id=item.product_id,
            quantity=item.quantity
        )

        db.add(order_item)

    db.commit()

    return {"message": "Order created successfully"}