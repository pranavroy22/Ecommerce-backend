from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True
        
    
class UserLogin(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    
    
class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    category: str
    stock: int


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float
    category: str
    stock: int

    class Config:
        from_attributes = True
        
        
class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int


class OrderCreate(BaseModel):
    items: list[OrderItemCreate]