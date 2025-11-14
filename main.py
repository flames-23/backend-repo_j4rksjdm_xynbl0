import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Product, Order, OrderItem

app = FastAPI(title="MK Store API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "MK Store API is running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

# Helpers
class ProductResponse(Product):
    id: str

class OrderResponse(Order):
    id: str

# Seed some example products if none exist
@app.post("/seed")
def seed_products():
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    count = db["product"].count_documents({})
    if count > 0:
        return {"seeded": False, "message": "Products already exist"}

    sample = [
        {
            "title": "MK Classic Tee",
            "description": "Soft cotton tee with classic MK logo.",
            "price": 24.99,
            "category": "T-Shirts",
            "in_stock": True,
            "image": "https://images.unsplash.com/photo-1520975930498-0d7d5121f9de?q=80&w=1200&auto=format&fit=crop",
            "sizes": ["S","M","L","XL"],
            "brand": "MK"
        },
        {
            "title": "MK Denim Jacket",
            "description": "Premium denim with modern fit.",
            "price": 79.99,
            "category": "Jackets",
            "in_stock": True,
            "image": "https://images.unsplash.com/photo-1520975661595-6453be3f7070?q=80&w=1200&auto=format&fit=crop",
            "sizes": ["S","M","L"],
            "brand": "MK"
        },
        {
            "title": "MK Joggers",
            "description": "Ultra comfy fleece joggers.",
            "price": 44.5,
            "category": "Pants",
            "in_stock": True,
            "image": "https://images.unsplash.com/photo-1520975916090-3105956dac38?q=80&w=1200&auto=format&fit=crop",
            "sizes": ["XS","S","M","L","XL"],
            "brand": "MK"
        }
    ]
    ids = []
    for p in sample:
        ids.append(create_document("product", p))
    return {"seeded": True, "count": len(ids), "ids": ids}

@app.get("/products", response_model=List[ProductResponse])
def list_products(category: Optional[str] = None, q: Optional[str] = None):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    query = {}
    if category:
        query["category"] = category
    docs = get_documents("product", query)
    result = []
    for d in docs:
        if q and q.lower() not in (d.get("title", "") + " " + d.get("description", "")).lower():
            continue
        d["id"] = str(d.pop("_id"))
        result.append(ProductResponse(**d))
    return result

class NewProduct(Product):
    pass

@app.post("/products", response_model=str)
def create_product(p: NewProduct):
    return create_document("product", p)

@app.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: str):
    doc = db["product"].find_one({"_id": ObjectId(product_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Product not found")
    doc["id"] = str(doc.pop("_id"))
    return ProductResponse(**doc)

@app.post("/orders", response_model=str)
def create_order(order: Order):
    return create_document("order", order)

@app.get("/orders", response_model=List[OrderResponse])
def list_orders():
    docs = get_documents("order")
    result = []
    for d in docs:
        d["id"] = str(d.pop("_id"))
        result.append(OrderResponse(**d))
    return result

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
