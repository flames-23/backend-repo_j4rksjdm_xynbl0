"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List

# Storefront user (not used for auth here, but kept as example)
class User(BaseModel):
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")
    image: Optional[str] = Field(None, description="Primary image URL")
    images: Optional[List[str]] = Field(default=None, description="Additional image URLs")
    sizes: Optional[List[str]] = Field(default=None, description="Available sizes (e.g., XS,S,M,L,XL)")
    brand: Optional[str] = Field(default="MK", description="Brand name")

class OrderItem(BaseModel):
    product_id: str = Field(..., description="Referenced product id")
    title: str = Field(..., description="Product title at time of order")
    price: float = Field(..., ge=0, description="Unit price at time of order")
    quantity: int = Field(..., ge=1, description="Quantity ordered")
    size: Optional[str] = Field(default=None, description="Selected size")
    image: Optional[str] = Field(default=None, description="Image thumbnail")

class CustomerInfo(BaseModel):
    name: str
    email: EmailStr
    address: str
    city: Optional[str] = None
    country: Optional[str] = None

class Order(BaseModel):
    """
    Orders collection schema
    Collection name: "order"
    """
    items: List[OrderItem]
    customer: CustomerInfo
    total: float = Field(..., ge=0)
    status: str = Field(default="pending")
