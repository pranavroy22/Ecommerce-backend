from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import os

from groq import Groq

from app.database import get_db
from app import models


router = APIRouter(
    prefix="/ai",
    tags=["AI"]
)


# 🔥 LOAD GROQ CLIENT
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


@router.post("/chat")
async def chat_with_ai(
    data: dict,
    db: Session = Depends(get_db)
):

    message = data.get("message")

    # 🔥 FETCH PRODUCTS FROM DATABASE
    products = db.query(models.Product).all()

    product_data = ""

    for product in products:

        product_data += f"""
        Name: {product.name}
        Description: {product.description}
        Price: ₹{product.price}
        Category: {product.category}
        Stock: {product.stock}
        """

    # 🔥 AI PROMPT
    prompt = f"""
    You are an AI shopping assistant
    for a modern ecommerce platform.

    ONLY recommend products
    from the provided database.

    PRODUCTS:
    {product_data}

    Rules:
    - Be friendly
    - Be concise
    - Mention prices
    - Recommend products smartly
    - Mention product names clearly
    - Help users compare products
    - Sound modern and professional

    User message:
    {message}
    """

    # 🔥 AI RESPONSE
    response = client.chat.completions.create(

        model="llama-3.3-70b-versatile",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return {
        "reply": response.choices[0].message.content
    }