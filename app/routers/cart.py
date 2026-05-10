from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Cart, CartItem, Product
from app.dependencies import get_current_user

router = APIRouter(prefix="/cart", tags=["Cart"])


# -------------------------
# Helper: Get or Create Cart
# -------------------------
def get_or_create_cart(db: Session, user_id: int):
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()

    if not cart:
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)

    return cart


# -------------------------
# Add to Cart
# -------------------------
@router.post("/add")
def add_to_cart(
    product_id: int,
    quantity: int = 1,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    cart = get_or_create_cart(db, current_user.id)

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if product.stock < quantity:
        raise HTTPException(status_code=400, detail="Not enough stock")

    existing_item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.product_id == product_id
    ).first()

    if existing_item:
        existing_item.quantity += quantity
    else:
        new_item = CartItem(
            cart_id=cart.id,
            product_id=product_id,
            quantity=quantity
        )
        db.add(new_item)

    db.commit()
    return {"message": "Item added to cart"}


# -------------------------
# Get Cart (OPTIMIZED 🔥)
# -------------------------
@router.get("/")
def get_cart(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    cart = get_or_create_cart(db, current_user.id)

    items_data = []
    total_price = 0

    for item in cart.items:
        product = item.product

        if product:
            item_total = product.price * item.quantity
            total_price += item_total

            items_data.append({
                "id": item.id,
                "product_id": product.id,
                "name": product.name,
                "price": product.price,
                "quantity": item.quantity,
                "total": item_total,
                "image_url": product.image_url
            })

    return {
        "id": cart.id,
        "user_id": cart.user_id,
        "total_price": total_price,
        "items": items_data
    }
# -------------------------
# Update Quantity (+ / -)
# -------------------------
@router.put("/update")
def update_cart_item(
    product_id: int,
    quantity: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    cart = get_or_create_cart(db, current_user.id)

    item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.product_id == product_id
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Remove if quantity <= 0
    if quantity <= 0:
        db.delete(item)
    else:
        product = item.product

        if product.stock < quantity:
            raise HTTPException(status_code=400, detail="Not enough stock")

        item.quantity = quantity

    db.commit()

    return {"message": "Cart updated"}


# -------------------------
# Remove Item
# -------------------------
@router.delete("/remove/{product_id}")
def remove_from_cart(
    product_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    cart = get_or_create_cart(db, current_user.id)

    item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.product_id == product_id
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not in cart")

    db.delete(item)
    db.commit()

    return {"message": "Item removed"}